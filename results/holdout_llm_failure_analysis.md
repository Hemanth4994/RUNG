# Holdout failure analysis: Gemini on matplotlib + numpy (67 wrong of 500)

**Provisional.** Every tag below comes from reading each issue's title and a 300-character excerpt, not the full
thread. The `outcome-only` tag in particular is a hypothesis about what maintainers did after the issue was filed.
Ten cases are marked `(check)`: open the link and read the thread before relying on the tag. These tags describe
the errors for the README. They are not used to change the predictor or the frozen settings.

## Tags

- **outcome-only**: the maintainers' label most likely reflects what happened after filing (answered as a usage
  question, closed with a docs example, found to be existing behaviour). The issue text alone does not decide it.
- **ambiguous label**: the text fits more than one label, or the taxonomy has no fitting class (for example PERF).
- **maintainer inconsistency**: the label disagrees with the issue's own title or content, or with how similar
  issues were labelled.
- **real miss**: the answer was visible in the title or excerpt and the model still got it wrong.

## Counts

| Tag | Cases | Share of the 67 |
|---|---|---|
| outcome-only | 42 | 63% |
| ambiguous label | 17 | 25% |
| real miss | 5 | 7% |
| maintainer inconsistency | 3 | 4% |

## What stands out

- **30 of the 67 are "predicted bug, maintainers said question".** These are issues filed with the `[Bug]` template
  that maintainers handled as support. Whether an issue is a bug or a usage question is often only settled after
  someone investigates, so it is not always decidable from the text the agent sees. This is why `bug` stays in review.
- **Most errors are in matplotlib** (52 of 67 errors; numpy 15). Check the per-repo issue counts in
  `scripts/check_data.py issues data/holdout_issues.jsonl` to turn these into rates.
- **The 3 errors on the auto-handled `docs` category** (cases 46 to 48) are all title-prefix versus content
  disagreements (`DOC:` or `BUG:` in the title, a different label from the maintainers). None is an obvious
  content mistake by the model.
- **Performance issues have no class.** Three numpy `PERF:` issues were labelled feature, bug and bug by the
  maintainers; the four-label taxonomy cannot express them.
- **Only 5 cases are clear misses** on evidence visible in the excerpt. That is not the same as
  "the model was fine": a wrong label applied automatically is still a wrong label, which is what the gate measures.

## Cases to read first

- [matplotlib/matplotlib#30389](https://github.com/matplotlib/matplotlib/issues/30389): predicted bug, maintainers question. ax.arrow default head: usage answer plausible
- [matplotlib/matplotlib#30866](https://github.com/matplotlib/matplotlib/issues/30866): predicted bug, maintainers question. calls itself a regression, but maintainers labelled support; check the thread
- [matplotlib/matplotlib#31717](https://github.com/matplotlib/matplotlib/issues/31717): predicted bug, maintainers question. scatter s is an area in points squared: usage answer plausible
- [matplotlib/matplotlib#31728](https://github.com/matplotlib/matplotlib/issues/31728): predicted bug, maintainers docs. title is a documentation build failure; model followed the [Bug] prefix
- [matplotlib/matplotlib#32471](https://github.com/matplotlib/matplotlib/issues/32471): predicted bug, maintainers question. reads like a real bug report; label may reflect the thread. Check it.
- [numpy/numpy#30919](https://github.com/numpy/numpy/issues/30919): predicted bug, maintainers question. classic floating-point determinant of a repeated-row matrix; visible in the excerpt
- [numpy/numpy#31625](https://github.com/numpy/numpy/issues/31625): predicted docs, maintainers bug. title says BUG: but it is about how the docs render; model's docs is the better reading
- [matplotlib/matplotlib#30336](https://github.com/matplotlib/matplotlib/issues/30336): predicted feature, maintainers docs. clear feature request; docs label likely reflects how it was closed (example). Check it.
- [matplotlib/matplotlib#30638](https://github.com/matplotlib/matplotlib/issues/30638): predicted feature, maintainers question. savefig.directory may already exist: usage answer plausible. Check it.
- [numpy/numpy#32136](https://github.com/numpy/numpy/issues/32136): predicted feature, maintainers bug. PERF issue: no performance class in the taxonomy

## All 67 cases

| # | Issue | Predicted → maintainers | Tag | Title | Note |
|---|---|---|---|---|---|
| 1 | [matplotlib/matplotlib#30041](https://github.com/matplotlib/matplotlib/issues/30041) | bug → question | outcome-only | [Bug]: qt_compat error in handling pyside6 Qt enumerations for pyplot | pyside6/Qt import failure: looks environment/version related |
| 2 | [matplotlib/matplotlib#30056](https://github.com/matplotlib/matplotlib/issues/30056) | bug → question | outcome-only | [Bug]: set_position for tick labels don't work | tick-label position is controlled by the locator/formatter; a usage answer is plausible |
| 3 | [matplotlib/matplotlib#30165](https://github.com/matplotlib/matplotlib/issues/30165) | bug → docs | ambiguous label | [Bug]: offset in transformed ellipse vertices | text itself says 'may be intended behaviour'; docs fix is defensible |
| 4 | [matplotlib/matplotlib#30230](https://github.com/matplotlib/matplotlib/issues/30230) | bug → feature | ambiguous label | [BUG]: Neither explicit data limit is respected when `constrained_layo | body says it was first an enhancement request, then a bug: both labels fit |
| 5 | [matplotlib/matplotlib#30308](https://github.com/matplotlib/matplotlib/issues/30308) | bug → question | outcome-only | [Bug]: Zorder issue for lines drawn with ConnectionPatch over inset_ax | zorder across axes/patches: usage answer plausible |
| 6 | [matplotlib/matplotlib#30389](https://github.com/matplotlib/matplotlib/issues/30389) | bug → question | outcome-only (check) | [Bug]: Arrow not drawing tip | ax.arrow default head: usage answer plausible |
| 7 | [matplotlib/matplotlib#30395](https://github.com/matplotlib/matplotlib/issues/30395) | bug → question | outcome-only | [Bug]: AutoDateLocator is not regular at the end of the month | date locator spacing: maintainers may have explained expected behaviour |
| 8 | [matplotlib/matplotlib#30501](https://github.com/matplotlib/matplotlib/issues/30501) | bug → question | outcome-only | [Bug]: Matplotlib crashes kernel on fresh (windows) install | kernel crash on fresh Windows install: environment |
| 9 | [matplotlib/matplotlib#30563](https://github.com/matplotlib/matplotlib/issues/30563) | bug → docs | outcome-only | [Bug]: 3D text does not respect rotation to make it parallel with a gi | 3D text rotation limitation, label likely reflects the reply |
| 10 | [matplotlib/matplotlib#30574](https://github.com/matplotlib/matplotlib/issues/30574) | bug → docs | ambiguous label | [Bug]: Unicode symbols encoded with `\u....` with mathtext raise Parse | docs example does not work: a bug in the docs or in mathtext |
| 11 | [matplotlib/matplotlib#30592](https://github.com/matplotlib/matplotlib/issues/30592) | bug → question | outcome-only | [Bug]: Default backend crashes in 3.10.6 works in 3.4.3 | backend crash across versions 3.4.3 -> 3.10.6: environment |
| 12 | [matplotlib/matplotlib#30617](https://github.com/matplotlib/matplotlib/issues/30617) | bug → feature | real miss | [ENH]: pyparsing 3.3.0a1 deprecation warnings | title says [ENH] and the body is deprecation warnings (maintenance), model said bug |
| 13 | [matplotlib/matplotlib#30637](https://github.com/matplotlib/matplotlib/issues/30637) | bug → question | outcome-only | [Bug]: axvline doesn't draw line correctly on second axes | axvline on twin/second axes: usage answer plausible |
| 14 | [matplotlib/matplotlib#30659](https://github.com/matplotlib/matplotlib/issues/30659) | bug → question | outcome-only | [Bug]: transforming FancyArrowPatch with connectionstyle to 3D has une | FancyArrowPatch to 3D: usage answer plausible |
| 15 | [matplotlib/matplotlib#30709](https://github.com/matplotlib/matplotlib/issues/30709) | bug → docs | ambiguous label | [Bug]: Mismatch in documented default behaviour of pcolormesh 'snap' | documented default differs from behaviour: docs or bug |
| 16 | [matplotlib/matplotlib#30722](https://github.com/matplotlib/matplotlib/issues/30722) | bug → question | outcome-only | Bars disappear when using rasterized=True in Axes.bar() with dense x-v | rasterized bars: usage answer plausible |
| 17 | [matplotlib/matplotlib#30748](https://github.com/matplotlib/matplotlib/issues/30748) | bug → question | outcome-only | [Bug]: matplotlib regerates font cache every single time ipython start | user's own startup script changes the font dir, cause not visible in the excerpt |
| 18 | [matplotlib/matplotlib#30831](https://github.com/matplotlib/matplotlib/issues/30831) | bug → docs+question | outcome-only | [Bug]: AttributeError: 'TimedAnimation' object has no attribute '_fram | uses a private attribute of TimedAnimation: usage |
| 19 | [matplotlib/matplotlib#30834](https://github.com/matplotlib/matplotlib/issues/30834) | bug → question | outcome-only | [Bug]: Thousands of minor ticks are generated after zoom out with home | user's own xlim_changed callback is in the loop: usage |
| 20 | [matplotlib/matplotlib#30866](https://github.com/matplotlib/matplotlib/issues/30866) | bug → question | outcome-only (check) | [Bug]: Incorrect offsets and scaling of EllipseCollection | calls itself a regression, but maintainers labelled support; check the thread |
| 21 | [matplotlib/matplotlib#30874](https://github.com/matplotlib/matplotlib/issues/30874) | bug → question | ambiguous label | [Bug]: Layout overlap with constrained_layout when adding long labels | vague text ('fragile', 'sometimes'), no clear repro in the excerpt |
| 22 | [matplotlib/matplotlib#31018](https://github.com/matplotlib/matplotlib/issues/31018) | bug → question | outcome-only | [Bug]: Axis elements cut off when saving figure to file with tight_lay | tight bbox with a long label: usage answer plausible |
| 23 | [matplotlib/matplotlib#31074](https://github.com/matplotlib/matplotlib/issues/31074) | bug → question | outcome-only | [Bug]:  Python matplotlib 3D drawing always overrides Quiver drawing i | mplot3d draws by artist order, not a z-buffer: known limitation |
| 24 | [matplotlib/matplotlib#31092](https://github.com/matplotlib/matplotlib/issues/31092) | bug → question | outcome-only | [Bug]: QuadMesh doesn't update face colors on set_color or set_facecol | QuadMesh colours come from the colormap: usage answer plausible |
| 25 | [matplotlib/matplotlib#31109](https://github.com/matplotlib/matplotlib/issues/31109) | bug → question | outcome-only | [Bug]: Non-bottom axes cannot apply fontdict to xticklabels via set_xt | shared-axis tick label handling: usage answer plausible |
| 26 | [matplotlib/matplotlib#31178](https://github.com/matplotlib/matplotlib/issues/31178) | bug → docs+question | outcome-only | [Bug]: fig.colorbar() requires plt.cm.ScalarMappable() object instead  | passes a colormap where a ScalarMappable is required: usage |
| 27 | [matplotlib/matplotlib#31197](https://github.com/matplotlib/matplotlib/issues/31197) | bug → question | outcome-only | [Bug]:  Second figure save differs in axes width for subplots with sha | tight_layout with shared axes: usage answer plausible |
| 28 | [matplotlib/matplotlib#31205](https://github.com/matplotlib/matplotlib/issues/31205) | bug → question | outcome-only | [Bug]: Minor shift of ax2 unexpectedly increases the height of ax1 in  | constrained layout interaction: usage answer plausible |
| 29 | [matplotlib/matplotlib#31406](https://github.com/matplotlib/matplotlib/issues/31406) | bug → feature | ambiguous label | [ENH]: [Bug]: secondary_xaxes().set_xlim/xbound should warn or raise t | title has both [ENH] and [Bug] |
| 30 | [matplotlib/matplotlib#31536](https://github.com/matplotlib/matplotlib/issues/31536) | bug → question | outcome-only | [Bug]: savefig() breaks FancyArrowPatch position on saved PNG when usi | patch coordinates vs dpi: usage answer plausible |
| 31 | [matplotlib/matplotlib#31717](https://github.com/matplotlib/matplotlib/issues/31717) | bug → question | outcome-only (check) | [Bug]: Marker sizes not consistent in Scatterplot | scatter s is an area in points squared: usage answer plausible |
| 32 | [matplotlib/matplotlib#31728](https://github.com/matplotlib/matplotlib/issues/31728) | bug → docs | real miss (check) | [Bug]: Doc build on 3.11 failure due to failed wx link | title is a documentation build failure; model followed the [Bug] prefix |
| 33 | [matplotlib/matplotlib#31971](https://github.com/matplotlib/matplotlib/issues/31971) | bug → docs+question | outcome-only | [Bug]: Changing GridSpec column/row ratios after axes creation does no | changing GridSpec ratios after creation is a known limitation |
| 34 | [matplotlib/matplotlib#32280](https://github.com/matplotlib/matplotlib/issues/32280) | bug → question | ambiguous label | compilation issues on windows | author writes 'my initial report was flawed'; build problem on a pre-release Python |
| 35 | [matplotlib/matplotlib#32471](https://github.com/matplotlib/matplotlib/issues/32471) | bug → question | outcome-only (check) | [Bug]: `bbox_inches='tight'` clips legend text on legends added by `Ax | reads like a real bug report; label may reflect the thread. Check it. |
| 36 | [matplotlib/matplotlib#32510](https://github.com/matplotlib/matplotlib/issues/32510) | bug → docs+question | outcome-only | [Bug]: broken_barh produces longer bars with smaller durations | broken_barh arguments: usage answer plausible |
| 37 | [matplotlib/matplotlib#32545](https://github.com/matplotlib/matplotlib/issues/32545) | bug → question | outcome-only | [Bug]: pcolormesh consider all shadings to be "flat" | pcolormesh shading with mismatched shapes: usage answer plausible |
| 38 | [numpy/numpy#30720](https://github.com/numpy/numpy/issues/30720) | bug → question | outcome-only | BUG: Boolean mask in fancy indexing would not work when some index is  | fancy indexing semantics: usage answer plausible |
| 39 | [numpy/numpy#30789](https://github.com/numpy/numpy/issues/30789) | bug → question | outcome-only | BUG: Inconsistent strides after indexing by list | strides after list indexing: usage answer plausible |
| 40 | [numpy/numpy#30884](https://github.com/numpy/numpy/issues/30884) | bug → question | outcome-only | BUG: f2py Arguments order in Python is different from Fortran | f2py moves intent(out) arguments: documented behaviour |
| 41 | [numpy/numpy#30919](https://github.com/numpy/numpy/issues/30919) | bug → question | real miss (check) | BUG: np.linalg.det() false outputs | classic floating-point determinant of a repeated-row matrix; visible in the excerpt |
| 42 | [numpy/numpy#31011](https://github.com/numpy/numpy/issues/31011) | bug → docs | ambiguous label | polynomial: `__truediv__` silently delegates to `__floordiv__`, violat | design/contract complaint; docs fix is defensible |
| 43 | [numpy/numpy#31038](https://github.com/numpy/numpy/issues/31038) | bug → question | outcome-only | BUG: `np.linspace` does not produce evenly spaced array with np.float3 | float32 linspace spacing: floating-point behaviour |
| 44 | [numpy/numpy#32161](https://github.com/numpy/numpy/issues/32161) | bug → feature | ambiguous label | PERF: np.isin is very slow for StringDType | PERF issue: the 4-label taxonomy has no performance class |
| 45 | [numpy/numpy#32299](https://github.com/numpy/numpy/issues/32299) | bug → docs | ambiguous label | DOC: Output of `RandomState.multinomial()` changed in v2.5.0 | DOC: prefix in the title but the body reports a behaviour change |
| 46 | [numpy/numpy#30786](https://github.com/numpy/numpy/issues/30786) | docs → bug | maintainer inconsistency | DOC: `np.save{,z}` does not make clear that it’s not suited for longte | title says DOC:, maintainers labelled bug |
| 47 | [numpy/numpy#31486](https://github.com/numpy/numpy/issues/31486) | docs → bug | ambiguous label | BUG/DOC: `numpy.ma.median` return dtype does not match documented beha | title says BUG/DOC: |
| 48 | [numpy/numpy#31625](https://github.com/numpy/numpy/issues/31625) | docs → bug | maintainer inconsistency (check) | BUG: Generalized ufunc docs render `->` in confusing way | title says BUG: but it is about how the docs render; model's docs is the better reading |
| 49 | [matplotlib/matplotlib#30051](https://github.com/matplotlib/matplotlib/issues/30051) | feature → question | outcome-only | [ENH]: Improve choropleth map support for geo datasets (individual cou | enhancement request that was likely redirected (support/elsewhere) |
| 50 | [matplotlib/matplotlib#30224](https://github.com/matplotlib/matplotlib/issues/30224) | feature → docs | real miss | Add an example of plotting error bars for grouped experimental data | asks for a gallery example, which is documentation; model said feature |
| 51 | [matplotlib/matplotlib#30336](https://github.com/matplotlib/matplotlib/issues/30336) | feature → docs | outcome-only (check) | [ENH]: Add ax.violinboxplot() for combined statistical visualization | clear feature request; docs label likely reflects how it was closed (example). Check it. |
| 52 | [matplotlib/matplotlib#30371](https://github.com/matplotlib/matplotlib/issues/30371) | feature → question | outcome-only | Request for Direct Legend Label Support for Contour Plots | feature request answered with an existing approach: likely |
| 53 | [matplotlib/matplotlib#30529](https://github.com/matplotlib/matplotlib/issues/30529) | feature → docs | real miss | Examples using Bivariate and Multivariate color maps | title is 'Examples using ...', which is documentation |
| 54 | [matplotlib/matplotlib#30623](https://github.com/matplotlib/matplotlib/issues/30623) | feature → question | outcome-only | [Bug]: Line3D is not represented correctly in a plot. | a design expectation filed as [Bug]; model's feature is reasonable |
| 55 | [matplotlib/matplotlib#30638](https://github.com/matplotlib/matplotlib/issues/30638) | feature → question | outcome-only (check) | Add support for specifying an initial directory for the “Save” dialog  | savefig.directory may already exist: usage answer plausible. Check it. |
| 56 | [matplotlib/matplotlib#30793](https://github.com/matplotlib/matplotlib/issues/30793) | feature → question | outcome-only | [ENH]: Setting custom display range in colorbar | ENH template, but the text reads as a support request |
| 57 | [matplotlib/matplotlib#31747](https://github.com/matplotlib/matplotlib/issues/31747) | feature → question | outcome-only | [MNT]: hardcoded zoom in view_init | view_init zoom may already be possible another way: usage |
| 58 | [matplotlib/matplotlib#32121](https://github.com/matplotlib/matplotlib/issues/32121) | feature → question | outcome-only | [MNT]: Please provide wheels for aarch64 | packaging/wheels request: support answer plausible |
| 59 | [matplotlib/matplotlib#32207](https://github.com/matplotlib/matplotlib/issues/32207) | feature → question | ambiguous label | [MNT]: Figure size as defined | design discussion about defaults; feature or question |
| 60 | [matplotlib/matplotlib#32381](https://github.com/matplotlib/matplotlib/issues/32381) | feature → docs | outcome-only | [ENH]: WSL support | feature request closed through documentation |
| 61 | [matplotlib/matplotlib#32409](https://github.com/matplotlib/matplotlib/issues/32409) | feature → docs | outcome-only | [ENH]: Expose KDE weights parameter in violinplot | feature request, docs label unexplained by the text |
| 62 | [numpy/numpy#31027](https://github.com/numpy/numpy/issues/31027) | feature → bug | ambiguous label | BUG/ENH: `np.sinc(np.inf)` generates warning and returns `nan` | title says BUG/ENH: |
| 63 | [numpy/numpy#32136](https://github.com/numpy/numpy/issues/32136) | feature → bug | ambiguous label (check) | PERF: np.sin(a, where=) is slower than computing the whole array | PERF issue: no performance class in the taxonomy |
| 64 | [numpy/numpy#32453](https://github.com/numpy/numpy/issues/32453) | feature → bug | ambiguous label | PERF: F->C order conversion thrashes the L3 cache | PERF issue: no performance class in the taxonomy |
| 65 | [numpy/numpy#33062](https://github.com/numpy/numpy/issues/33062) | feature → bug | ambiguous label | ENH: linalg: Consider improving accuracy of 2x2 det using Kahan's algo | title says ENH: but reports catastrophic error (accuracy bug) |
| 66 | [matplotlib/matplotlib#31156](https://github.com/matplotlib/matplotlib/issues/31156) | question → docs | maintainer inconsistency | Spam | the issue is spam filed with the docs template; no correct label exists |
| 67 | [matplotlib/matplotlib#32145](https://github.com/matplotlib/matplotlib/issues/32145) | question → feature | ambiguous label | [ENH]: Missing documentation (or functional) info on how to create hyp | 'missing documentation (or functional) info': docs, feature or question |
