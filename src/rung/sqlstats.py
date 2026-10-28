"""DuckDB / SQL layer for Rung: the same numbers as the Python code, written as SQL.

    python -m rung.sqlstats stats    data/records_llm.jsonl
    python -m rung.sqlstats backtest data/records_llm.jsonl [--max-error 0.05 --min-n 30]
    python -m rung.sqlstats compare  keyword=data/records_baseline.jsonl llm=data/records_llm.jsonl
    python -m rung.sqlstats quality  data/issues.jsonl --preds llm=data/pred_llm.jsonl

Why this exists: the statistics in stats.py / backtest.py are easy to trust because they are short
Python. Re-deriving them in SQL and *testing that both give identical numbers* (tests/test_sqlstats.py)
shows the logic is understood, not copied, and gives a data-engineering view (quality checks,
joins on ids) of the same pipeline.

Notes
-----
* Ties: Python's sort is stable, so records with the same timestamp keep file order. The SQL numbers
  rows in file order first and orders by (ts, file_row), so train/test splits match exactly.
* Parameters ($z, $cut, ...) are bound as DOUBLE/BIGINT, never written as SQL literals, because
  DuckDB reads a literal like 1.645 as DECIMAL, which would not match Python's float arithmetic.
* The 'bound <= max_error' promotion test compares floats; Python and SQL can in principle differ in
  the last bit exactly at the boundary. The tests check parity on realistic data, not on that edge.
"""
from __future__ import annotations

import argparse
import sys

try:
    import duckdb
except ImportError:          # the rest of Rung does not need DuckDB
    duckdb = None

Z_95_ONE_SIDED = 1.645

REC_COLS = "{'id':'VARCHAR','ts':'VARCHAR','category':'VARCHAR','correct':'BOOLEAN'}"
ISSUE_COLS = "{'id':'VARCHAR','repo':'VARCHAR','created_at':'VARCHAR','human_labels':'VARCHAR[]'}"
ID_COLS = "{'id':'VARCHAR'}"


def _require():
    if duckdb is None:
        raise ImportError("rung.sqlstats needs DuckDB: pip install duckdb")


def _connect(con=None):
    if con is not None:
        return con
    _require()
    return duckdb.connect()


# --- SQL, kept as readable constants -------------------------------------------------------

# One row per category: n, errors, error rate, and the one-sided Wilson upper bound.
# Same operation order as stats.wilson_upper.  {src} is a table name or "(subquery)".
STATS_SQL = """
WITH c AS (
    SELECT category, count(*) AS n, sum(CASE WHEN correct THEN 0 ELSE 1 END) AS errors
    FROM {src}
    GROUP BY category
), p AS (
    SELECT category, n, errors, CAST(errors AS DOUBLE) / n AS p FROM c
)
SELECT category, n, errors, p AS error_rate,
       least(CAST(1 AS DOUBLE),
             (p + $z * $z / (2 * n) + $z * sqrt(p * (1 - p) / n + $z * $z / (4 * n * n)))
             / (1 + $z * $z / n)) AS upper_bound
FROM p
ORDER BY category
"""

# Promotion rule from policy.decide: enough cases AND a low enough upper bound.
PROMOTED_SQL = """
SELECT category FROM ({stats}) WHERE n >= $min_n AND upper_bound <= $max_error ORDER BY category
"""

# Records in file order, with a parsed timestamp.
LOAD_RECORDS_SQL = """
CREATE OR REPLACE TEMP TABLE {table} AS
SELECT row_number() OVER () AS file_row, id, CAST(ts AS TIMESTAMPTZ) AS ts, category, correct
FROM read_json($path, format='newline_delimited', columns=%s)
""" % REC_COLS

# Keep the first row per id (file order), like Python's "first duplicate wins".
DEDUP_SQL = """
CREATE OR REPLACE TEMP TABLE {dst} AS
SELECT * FROM {src} QUALIFY row_number() OVER (PARTITION BY id ORDER BY file_row) = 1
"""

LOAD_ISSUES_SQL = """
CREATE OR REPLACE TEMP TABLE issues AS
SELECT row_number() OVER () AS file_row, id,
       COALESCE(repo, regexp_replace(id, '#[^#]*$', '')) AS repo,
       NULLIF(created_at, '') AS created_at,
       TRY_CAST(NULLIF(created_at, '') AS TIMESTAMPTZ) AS ts,
       human_labels
FROM read_json($path, format='newline_delimited', columns=%s)
""" % ISSUE_COLS


def _load_records(con, table: str, path) -> None:
    # .replace, not .format: the column map in the template contains literal braces
    con.execute(LOAD_RECORDS_SQL.replace("{table}", table), {"path": str(path)})


def _rows(con, sql: str, params: dict | None = None) -> list[dict]:
    cur = con.execute(sql, params or {})
    names = [d[0] for d in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]


# --- 1. per-category evidence --------------------------------------------------------------

def category_stats_sql(records_path, z: float = Z_95_ONE_SIDED, con=None) -> list[dict]:
    con = _connect(con)
    _load_records(con, "recs", records_path)
    return _rows(con, STATS_SQL.format(src="recs"), {"z": float(z)})


# --- 2. time-ordered backtest ----------------------------------------------------------------

def temporal_backtest_sql(records_path, max_error: float = 0.05, min_n: int = 30,
                          train_frac: float = 0.6, z: float = Z_95_ONE_SIDED, con=None) -> dict:
    """Decide on the earliest `train_frac` of records (by ts, ties in file order), score on the rest."""
    con = _connect(con)
    _load_records(con, "recs", records_path)
    con.execute("CREATE OR REPLACE TEMP TABLE ordered AS "
                "SELECT *, row_number() OVER (ORDER BY ts, file_row) AS rn FROM recs")
    total = con.execute("SELECT count(*) FROM ordered").fetchone()[0]
    # floor(total * frac) is the same IEEE multiply as Python's int(len(recs) * train_frac)
    cut = con.execute("SELECT CAST(floor(count(*) * $f) AS BIGINT) FROM ordered",
                      {"f": float(train_frac)}).fetchone()[0]

    train = STATS_SQL.format(src="(SELECT * FROM ordered WHERE rn <= $cut)")
    promoted = [r[0] for r in con.execute(
        PROMOTED_SQL.format(stats=train),
        {"z": float(z), "cut": int(cut), "min_n": int(min_n), "max_error": float(max_error)}).fetchall()]

    per_cat = {}
    if promoted:
        for r in _rows(con, """
            SELECT category, count(*) AS n, sum(CASE WHEN correct THEN 0 ELSE 1 END) AS errors
            FROM ordered WHERE rn > $cut AND list_contains($promoted, category)
            GROUP BY category""", {"cut": int(cut), "promoted": promoted}):
            per_cat[r["category"]] = (r["n"], r["errors"])
    auto_n = sum(n for n, _ in per_cat.values())
    auto_err = sum(e for _, e in per_cat.values())
    n_test = total - cut
    return {
        "n_train": int(cut), "n_test": int(n_test), "promoted": promoted,
        "auto_n": int(auto_n), "auto_errors": int(auto_err),
        "coverage": auto_n / n_test if n_test else 0.0,
        "auto_error_rate": auto_err / auto_n if auto_n else 0.0,
        "false_promotions": sorted(c for c, (n, e) in per_cat.items() if n > 0 and e / n > max_error),
    }


# --- 3. fair comparison between predictors -----------------------------------------------------

def compare_on_common_ids(named_records: dict[str, str], z: float = Z_95_ONE_SIDED, con=None) -> dict:
    """Per-category stats for each file, restricted to ids present in ALL files (first row per id)."""
    con = _connect(con)
    names = list(named_records)
    counts = {"rows": {}, "unique_ids": {}}
    for i, name in enumerate(names):
        _load_records(con, f"recs_{i}", named_records[name])
        con.execute(DEDUP_SQL.format(dst=f"d_{i}", src=f"recs_{i}"))
        counts["rows"][name] = con.execute(f"SELECT count(*) FROM recs_{i}").fetchone()[0]
        counts["unique_ids"][name] = con.execute(f"SELECT count(*) FROM d_{i}").fetchone()[0]
    con.execute("CREATE OR REPLACE TEMP TABLE common AS " +
                " INTERSECT ".join(f"SELECT id FROM d_{i}" for i in range(len(names))))
    counts["common_ids"] = con.execute("SELECT count(*) FROM common").fetchone()[0]
    stats = {name: _rows(con, STATS_SQL.format(src=f"(SELECT * FROM d_{i} WHERE id IN (SELECT id FROM common))"),
                         {"z": float(z)})
             for i, name in enumerate(names)}
    return {"counts": counts, "stats": stats}


# --- 4. data-quality report ------------------------------------------------------------------

def quality_report(issues_path, pred_paths: dict[str, str] | None = None, con=None) -> dict:
    con = _connect(con)
    con.execute(LOAD_ISSUES_SQL, {"path": str(issues_path)})
    con.execute(DEDUP_SQL.format(dst="issues_u", src="issues"))
    one = lambda sql: con.execute(sql).fetchone()[0]          # noqa: E731
    rows, unique = one("SELECT count(*) FROM issues"), one("SELECT count(*) FROM issues_u")
    report = {
        "rows": rows,
        "unique_ids": unique,
        "duplicate_ids": one("SELECT count(*) FROM (SELECT id FROM issues GROUP BY id HAVING count(*) > 1)"),
        "extra_rows_from_duplicates": rows - unique,
        "missing_created_at": one("SELECT count(*) FROM issues WHERE created_at IS NULL"),
        "missing_human_labels": one("SELECT count(*) FROM issues "
                                    "WHERE human_labels IS NULL OR len(human_labels) = 0"),
    }
    report["per_repo"] = {r["repo"]: {k: r[k] for k in ("rows", "unique", "first_created", "last_created")}
                          for r in _rows(con, """
        SELECT a.repo, a.rows, b.unique, b.first_created, b.last_created
        FROM (SELECT repo, count(*) AS rows FROM issues GROUP BY repo) a
        JOIN (SELECT repo, count(*) AS unique,
                     arg_min(created_at, ts) FILTER (WHERE ts IS NOT NULL) AS first_created,
                     arg_max(created_at, ts) FILTER (WHERE ts IS NOT NULL) AS last_created
              FROM issues_u GROUP BY repo) b USING (repo)
        ORDER BY a.repo""")}
    mix: dict[str, dict[str, int]] = {}
    for r in _rows(con, """
        SELECT repo, label, count(*) AS n FROM issues_u, UNNEST(human_labels) AS t(label)
        GROUP BY repo, label ORDER BY repo, label"""):
        mix.setdefault(r["repo"], {})[r["label"]] = r["n"]
    report["label_mix"] = mix
    preds = {}
    for i, (name, path) in enumerate((pred_paths or {}).items()):
        con.execute(f"CREATE OR REPLACE TEMP TABLE p_{i} AS SELECT row_number() OVER () AS file_row, id "
                    f"FROM read_json($path, format='newline_delimited', columns={ID_COLS})", {"path": str(path)})
        con.execute(DEDUP_SQL.format(dst=f"pu_{i}", src=f"p_{i}"))
        preds[name] = {
            "rows": one(f"SELECT count(*) FROM p_{i}"),
            "unique_ids": one(f"SELECT count(*) FROM pu_{i}"),
            "issues_missing_from_preds": one(f"SELECT count(*) FROM issues_u WHERE id NOT IN (SELECT id FROM pu_{i})"),
            "pred_ids_not_in_issues": one(f"SELECT count(*) FROM pu_{i} WHERE id NOT IN (SELECT id FROM issues_u)"),
        }
    report["predictions"] = preds
    return report


# --- CLI -----------------------------------------------------------------------------------

def _table(rows: list[dict], cols: list[str]) -> str:
    def fmt(v):
        return f"{v:.4f}" if isinstance(v, float) else str(v)
    cells = [[fmt(r[c]) for c in cols] for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in cells)) if cells else len(c) for i, c in enumerate(cols)]
    line = lambda vals: "  ".join(v.ljust(w) for v, w in zip(vals, widths))   # noqa: E731
    return "\n".join([line(cols)] + [line(row) for row in cells])


def _pairs(items: list[str]) -> dict[str, str]:
    out = {}
    for it in items:
        if "=" not in it:
            raise SystemExit(f"expected name=path, got {it!r}")
        k, v = it.split("=", 1)
        out[k] = v
    return out


def main(argv: list[str] | None = None) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(prog="rung.sqlstats")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stats"); s.add_argument("records")
    b = sub.add_parser("backtest"); b.add_argument("records")
    b.add_argument("--max-error", type=float, default=0.05); b.add_argument("--min-n", type=int, default=30)
    c = sub.add_parser("compare"); c.add_argument("named", nargs="+")
    q = sub.add_parser("quality"); q.add_argument("issues"); q.add_argument("--preds", nargs="*", default=[])
    a = ap.parse_args(argv)

    if a.cmd == "stats":
        print(_table(category_stats_sql(a.records), ["category", "n", "errors", "error_rate", "upper_bound"]))
    elif a.cmd == "backtest":
        for k, v in temporal_backtest_sql(a.records, a.max_error, a.min_n).items():
            print(f"{k}: {v}")
    elif a.cmd == "compare":
        res = compare_on_common_ids(_pairs(a.named))
        print("counts:", res["counts"])
        for name, rows in res["stats"].items():
            print(f"\n[{name}] on common ids")
            print(_table(rows, ["category", "n", "errors", "error_rate", "upper_bound"]))
    elif a.cmd == "quality":
        rep = quality_report(a.issues, _pairs(a.preds))
        for k, v in rep.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
