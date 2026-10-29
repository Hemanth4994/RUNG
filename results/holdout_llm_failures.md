# Wrong predictions: 67 of 500

Tag each: `ambiguous label` | `maintainer inconsistency` | `real miss`

## Predicted vs maintainers' label(s)

| predicted | maintainers | count |
|---|---|---|
| bug | question | 30 |
| feature | question | 8 |
| bug | docs | 7 |
| feature | docs | 5 |
| bug | docs+question | 4 |
| bug | feature | 4 |
| feature | bug | 4 |
| docs | bug | 3 |
| question | feature | 1 |
| question | docs | 1 |

## Cases

### 1. matplotlib/matplotlib#30041  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30041
Title: [Bug]: qt_compat error in handling pyside6 Qt enumerations for pyplot
Body: ### Bug summary pyplot cannot be imported. Raises an error pertaining to converting Qt Enumerations to integers. ### Code for reproduction ```Python import matplotlib.pyplot as plt """ Error is thrown on import """ # addendum import matplotlib # This also produces the same error (same source) matplo ...
Tag: 

### 2. matplotlib/matplotlib#30056  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30056
Title: [Bug]: set_position for tick labels don't work
Body: ### Bug summary Sometimes, the axis tick labels overlaps. In such cases, manually adjusting their positions slightly is one solution. However, I found that this doesn't seem to work. Here is a simple example. I simulated a situation where the text would overlap by setting a smaller figure size. ```P ...
Tag: 

### 3. matplotlib/matplotlib#30165  predicted **bug**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30165
Title: [Bug]: offset in transformed ellipse vertices
Body: ### Bug summary I was following [this](https://matplotlib.org/stable/gallery/statistics/confidence_ellipse.html)sexample on drawing ellipses and wanted to get the vertices out. Calling Ellipse.get_vertices() returns the untransformed vertices which may be intended behaviour, but I also seem to be un ...
Tag: 

### 4. matplotlib/matplotlib#30230  predicted **bug**, maintainers ['feature']
https://github.com/matplotlib/matplotlib/issues/30230
Title: [BUG]: Neither explicit data limit is respected when `constrained_layout` is used together with `set_aspect(..., "datalim")`
Body: *Edit: This description was written when this was still considered an enhancement request. It turned out that the feature in question already is available, but in certain circumstances doesn't work correctly.* ### Problem This is an extension of #28673. The problem is that once a user has request `s ...
Tag: 

### 5. matplotlib/matplotlib#30308  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30308
Title: [Bug]: Zorder issue for lines drawn with ConnectionPatch over inset_axes/plot axes
Body: ### Bug summary If `ConnectionPatch` zorder is not set to 0, the line drawn will always be on top of the `inset_axes` axes or the primary plot axes (in this example the x-axis on the plots) even if the zorder of the plot axes is higher than that of the `ConnectionPatch`. In this example, the line dr ...
Tag: 

### 6. matplotlib/matplotlib#30389  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30389
Title: [Bug]: Arrow not drawing tip
Body: ### Bug summary When I try to draw an arrow, it doesn't have a tip. ```python import matplotlib.pyplot as plt fig, ax = plt.subplots(figsize=(3, 3)) ax.arrow(0,1,1,1,) plt.show() ``` <img width="300" height="300" alt="Image" src="https://github.com/user-attachments/assets/a6733a3a-6677-4978-890f-3ca ...
Tag: 

### 7. matplotlib/matplotlib#30395  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30395
Title: [Bug]: AutoDateLocator is not regular at the end of the month
Body: ### Bug summary When plotting by default at the end of a month, the date locator seems to jump a day, creating non regularly spaced ticks. ### Code for reproduction ```Python To create the plot which cause problem import matplotlib.pyplot as plt import pandas as pd x = pd.to_datetime(['2024-07-29 00 ...
Tag: 

### 8. matplotlib/matplotlib#30501  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30501
Title: [Bug]: Matplotlib crashes kernel on fresh (windows) install
Body: ### Bug summary Hello, I recently encountered a problem whereby Matplotlib crashes the jupyter kernel on my windows machine. I can reproduce it in a fresh environment. ### Code for reproduction Steps: 1) Install python from miniforge 2) Install jupyter and matplotlib with `mamba install jupyter note ...
Tag: 

### 9. matplotlib/matplotlib#30563  predicted **bug**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30563
Title: [Bug]: 3D text does not respect rotation to make it parallel with a given zdir axis
Body: ### Bug summary 3D text rotated along a given axis, e.g. `zdir = "x"` or `zdir = (1, 0, 0)`, is always rotated roughly 60 degrees and does not respect the `rotation` argument for changing the orientation to e.g. `0` or `90` to be parallel with the specified axis. ### Code for reproduction ```Python ...
Tag: 

### 10. matplotlib/matplotlib#30574  predicted **bug**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30574
Title: [Bug]: Unicode symbols encoded with `\u....` with mathtext raise ParseFatalException
Body: ### Bug summary The [documentation](https://matplotlib.org/stable/users/explain/text/mathtext.html#symbols) states that symbols can be encoded in mathtext with the following example: ```python r'$\u23ce$' ``` But this does not work and raises a ParseFatalException. ### Code for reproduction ```Pytho ...
Tag: 

### 11. matplotlib/matplotlib#30592  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30592
Title: [Bug]: Default backend crashes in 3.10.6 works in 3.4.3
Body: ### Bug summary The following simple program crashes on my Linux system running python 3.11 and matplotlib 3.10.6, but works using matplotlib 3.4.3 ### Code for reproduction ```Python import matplotlib.pyplot as plt import matplotlib.patches as patches # Create a figure and axes fig, ax = plt.subplo ...
Tag: 

### 12. matplotlib/matplotlib#30617  predicted **bug**, maintainers ['feature']
https://github.com/matplotlib/matplotlib/issues/30617
Title: [ENH]: pyparsing 3.3.0a1 deprecation warnings
Body: ### Problem ``` pip install --pre matplotlib ``` matplotlib 3.10.6 ``` python -W always -c "import matplotlib" .../python3.12/site-packages/matplotlib/_fontconfig_pattern.py:64: DeprecationWarning: 'oneOf' deprecated - use 'one_of' prop = Group((name + Suppress("=") + comma_separated(value)) | oneOf ...
Tag: 

### 13. matplotlib/matplotlib#30637  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30637
Title: [Bug]: axvline doesn't draw line correctly on second axes
Body: ### Bug summary Looks like `axvline` doesn't work on the second axes correctly (See code). Also if I set ymin=0, ymax=10, ylim=(-1, 11) it draw line from bottom to the top of the axes rather than from 0 to 10. ### Code for reproduction ```Python import matplotlib.pyplot as plt fig, axes = plt.subplo ...
Tag: 

### 14. matplotlib/matplotlib#30659  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30659
Title: [Bug]: transforming FancyArrowPatch with connectionstyle to 3D has unexpected result
Body: ### Bug summary I'm trying to draw a curved FancyArrowPatch to annotate an angle in a 3D plot. When I try transform FancyArrowPatch to 3D and use the arc3 connectionstyle, it seems that the transform isn't applied correctly. When I do this without a connectionstyle, I get the expected result. ### Co ...
Tag: 

### 15. matplotlib/matplotlib#30709  predicted **bug**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30709
Title: [Bug]: Mismatch in documented default behaviour of pcolormesh 'snap'
Body: ### Bug summary The [documentation for pcolormesh](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html) states the default behaviour for **snap** is _**False**_. Since a supposed temporary addition of **pcolormesh.snap** to the default rcParams under https://github.com/mat ...
Tag: 

### 16. matplotlib/matplotlib#30722  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30722
Title: Bars disappear when using rasterized=True in Axes.bar() with dense x-values
Body: Hi, For a specific purpose, I need to draw a bar chart using `Axes.bar()` where the x-axis ranges from 0 to 900, with a figure width fixed at 3.5 inches. I make sure that each x-coordinate has a corresponding y-value, so the final chart should consist of many bars without any missing ones. Since I w ...
Tag: 

### 17. matplotlib/matplotlib#30748  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30748
Title: [Bug]: matplotlib regerates font cache every single time ipython starts
Body: ### Bug summary I have the following code in `~/.ipython/profile_default/startup/00-load_modules.py` to be able to use fonts in `~/Library/Fonts` in matplotlib. ```python import os # Use my fonts, which are not found by default by matplotlib user_font_dir = os.path.join(os.environ['HOME'], 'Library/ ...
Tag: 

### 18. matplotlib/matplotlib#30831  predicted **bug**, maintainers ['docs', 'question']
https://github.com/matplotlib/matplotlib/issues/30831
Title: [Bug]: AttributeError: 'TimedAnimation' object has no attribute '_framedata'
Body: ### Bug summary Hi, I try to use TimedAnimation class to manage a figure which should plot some sensor data sent in synchronized way, but an AttributeError occurs and I see that in the documentation there is no "_framedata" parameter to set. ### Code for reproduction ```Python # The code I try to ru ...
Tag: 

### 19. matplotlib/matplotlib#30834  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30834
Title: [Bug]: Thousands of minor ticks are generated after zoom out with home button in toolbar
Body: ### Bug summary I use major ticks and minor ticks and adopt them after zooming with "ax.callbacks.connect('xlim_changed', self._ax_scaled)". When zooming in very deep and then zooming out in one step with the "home" button of toolbar I got the message "Locator attempting to generate 50003 ticks ([-0 ...
Tag: 

### 20. matplotlib/matplotlib#30866  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30866
Title: [Bug]: Incorrect offsets and scaling of EllipseCollection
Body: ### Bug summary This is a regression bug. The position and scaling of `EllipseCollection` do not follow the specification of `offsets`. ### Code for reproduction ```Python import matplotlib.pyplot as plt import numpy as np from matplotlib.collections import EllipseCollection x = np.arange(2) y = np. ...
Tag: 

### 21. matplotlib/matplotlib#30874  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30874
Title: [Bug]: Layout overlap with constrained_layout when adding long labels
Body: ### Bug summary I’ve noticed that layout handling can be fragile when combining constrained_layout with colorbars and longer labels/titles, On my setup, labels or the title can overlap or get clipped. Small changes like font size or figure size sometimes change the behavior. Switching to tight_layou ...
Tag: 

### 22. matplotlib/matplotlib#31018  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31018
Title: [Bug]: Axis elements cut off when saving figure to file with tight_layout/bbox_inches
Body: ### Bug summary When saving a figure with a very long x-axis label, the text is cut off. This occurs with both fig.tight_layout() and bbox_inches='tight' selected. This previously worked with older versions. ### Code for reproduction ```Python import matplotlib matplotlib.use('Agg') import matplotli ...
Tag: 

### 23. matplotlib/matplotlib#31074  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31074
Title: [Bug]:  Python matplotlib 3D drawing always overrides Quiver drawing in 3D coordinate system with contour drawing, setting Zorder and adjusting the order of drawing are invalid
Body: ### Bug summary Python matplotlib 3D drawing always overrides Quiver drawing in 3D coordinate system with contour drawing, setting Zorder and adjusting the order of drawing are invalid ### Code for reproduction ```Python lon = gh_grid.lon.values lat = gh_grid.lat.values lat_start_index = int(round(( ...
Tag: 

### 24. matplotlib/matplotlib#31092  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31092
Title: [Bug]: QuadMesh doesn't update face colors on set_color or set_facecolor
Body: ### Bug summary `QuadMesh` which returned by `pcolormesh` does not update face colors. ### Code for reproduction ```Python import numpy as np import matplotlib as mpl from matplotlib import pyplot as plt print(mpl.__version__) f = plt.figure() cmap= plt.get_cmap('rainbow') X,Y = np.meshgrid(np.arang ...
Tag: 

### 25. matplotlib/matplotlib#31109  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31109
Title: [Bug]: Non-bottom axes cannot apply fontdict to xticklabels via set_xticklabels in subplots with sharex=True
Body: ### Bug summary When creating subplots with `sharex=True`, I expect both xticks and xticklabels can be accessed and modified by `axs[0]` and `axs[1]`. In the example below, the positions and labels of xticks can be set by `axs[0]` and `axs[1]`, but `axs[0]` cannot set the fontsize of the xticklabels ...
Tag: 

### 26. matplotlib/matplotlib#31178  predicted **bug**, maintainers ['docs', 'question']
https://github.com/matplotlib/matplotlib/issues/31178
Title: [Bug]: fig.colorbar() requires plt.cm.ScalarMappable() object instead of matplotlib.colors.ListedColormap() as it lacks .get_cmap()
Body: ### Bug summary Hi, I wonder why always people specify a list o colors but then apply `np.linspace(0, 1, N)` over it. This then shifts the colors a bit and some colors are then unused, for example a color between `-4` and `-5`. I want to avoid the https://gist.github.com/jakevdp/91077b0cae40f8f8244a ...
Tag: 

### 27. matplotlib/matplotlib#31197  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31197
Title: [Bug]:  Second figure save differs in axes width for subplots with shared y-axis and tight layout
Body: ### Bug summary I try to save the subplots with `sharey=True` and `tight_layout=True` twice. But the second save is different from the first save in the axes width. ### Code for reproduction ```Python import matplotlib.pyplot as plt import numpy as np N_points = 100000 n_bins = 20 rng = np.random.de ...
Tag: 

### 28. matplotlib/matplotlib#31205  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31205
Title: [Bug]: Minor shift of ax2 unexpectedly increases the height of ax1 in constrained layout
Body: ### Bug summary The bug occurs when I first save the figure as 'plot1.png', then slightly adjust the position of `ax2`, and save the updated figure as 'plot2.png'. It seems the constrained layout engine accidentally over-adjusts the height of `ax1`, which causes the x-label of `ax1` to be obscured b ...
Tag: 

### 29. matplotlib/matplotlib#31406  predicted **bug**, maintainers ['feature']
https://github.com/matplotlib/matplotlib/issues/31406
Title: [ENH]: [Bug]: secondary_xaxes().set_xlim/xbound should warn or raise that it is ineffective
Body: ### Problem Changing the limits of a main axes will update the secondary axes' limits (at draw time), but changing the limits of a secondary axes has silently no effect (they get again overwritten by the (converted) main limits at draw time, in SecondaryAxes._set_lims). This should at least warn or ...
Tag: 

### 30. matplotlib/matplotlib#31536  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31536
Title: [Bug]: savefig() breaks FancyArrowPatch position on saved PNG when using custom DPI
Body: ### Bug summary Heyho, I encountered an error with patches (FancyArrowPatch). When i draw FancyArrowPatches into a figure and save the figures with savefig(), the patches shift around to different positions depending on my set `dpi=`parameter as shown by the following screenshots, produced by code u ...
Tag: 

### 31. matplotlib/matplotlib#31717  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31717
Title: [Bug]: Marker sizes not consistent in Scatterplot
Body: ### Bug summary When plotting size values like [1.5, 3.0, 4.5, 6.0] in a scatterplot, the actual sizes plotted (area of the square) on the screen / printer are [3.61, 6.76, 13.69, 27] (1 : 1.87 : 3.79 : 7.48) which is an unacceptable difference to the required 1 : 2 : 4 : 8 relation. ### Code for re ...
Tag: 

### 32. matplotlib/matplotlib#31728  predicted **bug**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/31728
Title: [Bug]: Doc build on 3.11 failure due to failed wx link
Body: ### Bug summary > WARNING: failed to reach any of the inventories with the following issues: /home/circleci/project/doc/gallery/user_interfaces/embedding_in_wx5_sgskip.rst:30: WARNING: py:class reference target not found: wx.App [ref.class] /home/circleci/project/doc/gallery/user_interfaces/embeddin ...
Tag: 

### 33. matplotlib/matplotlib#31971  predicted **bug**, maintainers ['docs', 'question']
https://github.com/matplotlib/matplotlib/issues/31971
Title: [Bug]: Changing GridSpec column/row ratios after axes creation does not update the figure layout
Body: ### Bug summary Updating a `GridSpec`'s width or height ratios after axes have already been added to it has no visible effect — the figure layout silently stays unchanged, even though the internal state is updated correctly. ### Code for reproduction ```Python import matplotlib.pyplot as plt import ...
Tag: 

### 34. matplotlib/matplotlib#32280  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/32280
Title: compilation issues on windows
Body: On Windows, using Python 3.15.0rc2: My initial report was flawed. But there appears to be a real problem. See below. <details> <br> ```console C:\Repos\leo-editor>python --version Python 3.15.0rc2 C:\Repos\leo-editor>python -m pip --version pip 26.2.1 from C:\Users\Dev\AppData\Local\Python\pythoncor ...
Tag: 

### 35. matplotlib/matplotlib#32471  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/32471
Title: [Bug]: `bbox_inches='tight'` clips legend text on legends added by `Axes.add_artist()`, even with ample canvas margin
Body: ### Bug summary When an `Axes` has more than one `Legend`, the common pattern being one legend added via `ax.legend()` (which `Axes` tracks internally) and additional ones attached via `ax.add_artist()` (since an axes can only have one "current" legend), saving with `bbox_inches='tight'` clips the l ...
Tag: 

### 36. matplotlib/matplotlib#32510  predicted **bug**, maintainers ['docs', 'question']
https://github.com/matplotlib/matplotlib/issues/32510
Title: [Bug]: broken_barh produces longer bars with smaller durations
Body: ### Bug summary The broken_barh method appears to reproduce ranges inconsistently: given two durations, the larger one appears smaller, and in some cases even disappears. ### Code for reproduction ```Python # example 1 fig, ax = plt.subplots() # broken_barh(xranges, (ypos, height)) ax.broken_barh([( ...
Tag: 

### 37. matplotlib/matplotlib#32545  predicted **bug**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/32545
Title: [Bug]: pcolormesh consider all shadings to be "flat"
Body: ### Bug summary Using a mesh where the dimensions are the same size as the data points, all alternative of shading "nearest" and "auto" are considered "flat" leading to a crash ### Code for reproduction ```Python x=np.arange(50) x[25:]*=2 y =np.arange(20) d=np.random.random((50,20)) X,Y =np.meshgrid ...
Tag: 

### 38. numpy/numpy#30720  predicted **bug**, maintainers ['question']
https://github.com/numpy/numpy/issues/30720
Title: BUG: Boolean mask in fancy indexing would not work when some index is essentially empty
Body: ### Describe the issue: When doing fancy indexing, boolean mask would result in error when some other array is essentially empty (i.e. either (int)[] or [False...]) ### Reproduce the code example: ```python import numpy as np a = np.empty((1,2)) a[[False],[True,True]] #or a[[],[True,True]], both sam ...
Tag: 

### 39. numpy/numpy#30789  predicted **bug**, maintainers ['question']
https://github.com/numpy/numpy/issues/30789
Title: BUG: Inconsistent strides after indexing by list
Body: ### Describe the issue: When indexing a matrix using a list of indices, a view is produced with inconsistent strides, that cannot be really detected in the C-API, as the array is declared as C_CONTIGUOUS and having stride == 1 element. ### Reproduce the code example: ```python R=np.ones((1,2)) print ...
Tag: 

### 40. numpy/numpy#30884  predicted **bug**, maintainers ['question']
https://github.com/numpy/numpy/issues/30884
Title: BUG: f2py Arguments order in Python is different from Fortran
Body: ### Describe the issue: After compiling a .so with f2py from a old Fortran code (around year 2000~), i wanted to use it in a Python script. I replaced all variables and names to letters since there's a safety concern. I apologize The subroutine in Fortran has this signature: ```fortran subroutine fo ...
Tag: 

### 41. numpy/numpy#30919  predicted **bug**, maintainers ['question']
https://github.com/numpy/numpy/issues/30919
Title: BUG: np.linalg.det() false outputs
Body: I have a 12 by 12 matrix that I am trying to reduce to an invertible square matrix. np.linalg.det(matrix) falsely determines that the det(matrix) is not equal to zero, when there are rows that repeat (ergo, [[1, 1], [1, 1]] but not this simple of a case). My code is: matrix = [ [-1, -1.7424000000000 ...
Tag: 

### 42. numpy/numpy#31011  predicted **bug**, maintainers ['docs']
https://github.com/numpy/numpy/issues/31011
Title: polynomial: `__truediv__` silently delegates to `__floordiv__`, violating Python's operator contract
Body: `Polynomial.__truediv__` (and all subclasses via `_polybase.py`) delegates unconditionally to `__floordiv__`: ```python # numpy/polynomial/_polybase.py, line 563 def __truediv__(self, other): if not isinstance(other, numbers.Number) or isinstance(other, bool): raise TypeError(...) return self.__floo ...
Tag: 

### 43. numpy/numpy#31038  predicted **bug**, maintainers ['question']
https://github.com/numpy/numpy/issues/31038
Title: BUG: `np.linspace` does not produce evenly spaced array with np.float32 inputs since `numpy 2.0`
Body: ### Describe the issue: Hello, I am currently facing an issue in my code which seems related to a `numpy.linspace` call to produce input data. When I check the diff of the results of `np.linspace`, they are not (exactly) evenly spaced. My test data comes from an array, read as float32. But I did not ...
Tag: 

### 44. numpy/numpy#32161  predicted **bug**, maintainers ['feature']
https://github.com/numpy/numpy/issues/32161
Title: PERF: np.isin is very slow for StringDType
Body: This is more-or-less the same issue as https://github.com/numpy/numpy/issues/14997 because both object arrays and stringdtype fall back to the `hasobject` path in the `_isin` helper: https://github.com/numpy/numpy/blob/30483388e8c07f1abd45b47c534801e9207d2643/numpy/lib/_arraysetops_impl.py#L910-L926 ...
Tag: 

### 45. numpy/numpy#32299  predicted **bug**, maintainers ['docs']
https://github.com/numpy/numpy/issues/32299
Title: DOC: Output of `RandomState.multinomial()` changed in v2.5.0
Body: ### Describe the issue: Despite the intention of #31238, it appears the output of `RandomState(seed).multinomial()` changed. ### Reproduce the code example: ```python import numpy as np p = np.asarray([0.5, 0., 0.5, 0., 0., 0.]) n = 2.0 size = 5 np.random.RandomState(1234).multinomial(n, p, size) `` ...
Tag: 

### 46. numpy/numpy#30786  predicted **docs**, maintainers ['bug']
https://github.com/numpy/numpy/issues/30786
Title: DOC: `np.save{,z}` does not make clear that it’s not suited for longterm storage
Body: ### Describe the issue: See title. Alternatively, numpy shouldn’t warn when reading a pickle file it wrote. ### Reproduce the code example: ```python import pickle import subprocess url = <edit to remove link to pickle> with urllib.request.urlopen(url) as con: true_scores_t_test, true_names_t_test = ...
Tag: 

### 47. numpy/numpy#31486  predicted **docs**, maintainers ['bug']
https://github.com/numpy/numpy/issues/31486
Title: BUG/DOC: `numpy.ma.median` return dtype does not match documented behavior
Body: ### Describe the issue: According to the documentation for [`ma.median`](https://numpy.org/doc/stable/reference/generated/numpy.ma.median.html#numpy-ma-median): Return data-type is `float64` for integers and floats smaller than `float64`, or the input data-type, otherwise. However, in the following ...
Tag: 

### 48. numpy/numpy#31625  predicted **docs**, maintainers ['bug']
https://github.com/numpy/numpy/issues/31625
Title: BUG: Generalized ufunc docs render `->` in confusing way
Body: ### Describe the issue: It's possible that this may related to fonts I have installed or something like that. I'm not completely sure, but it's possible that others won't experience this. On the development docs (but not the stable docs), the arrows render as full arrows for me: <img width="917" hei ...
Tag: 

### 49. matplotlib/matplotlib#30051  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30051
Title: [ENH]: Improve choropleth map support for geo datasets (individual country/region separation)
Body: ### Problem ### Problem While working with geospatial datasets and plotting choropleth maps using GeoPandas and Matplotlib, I found that Matplotlib lacks high-level support for customizing individual geographic regions like countries or states. For example, with this code: ```python # Defining the c ...
Tag: 

### 50. matplotlib/matplotlib#30224  predicted **feature**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30224
Title: Add an example of plotting error bars for grouped experimental data
Body: ### Add grouped error‑bar plot example to gallery Add a demo script to `galleries/examples/statistics/errorbar_features.py` showing how to plot mean ± standard error for multiple groups. ### Reason Error bars are important in data analysis to communicate uncertainty. A clear grouped example helps an ...
Tag: 

### 51. matplotlib/matplotlib#30336  predicted **feature**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30336
Title: [ENH]: Add ax.violinboxplot() for combined statistical visualization
Body: ### Problem matplotlib lacks a direct method to create a plot that combines a violin plot (to show data distribution) and a box plot (to show summary statistics). This is a very common and powerful visualization for statistical analysis. Currently, users must manually overlay ax.violinplot() and ax. ...
Tag: 

### 52. matplotlib/matplotlib#30371  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30371
Title: Request for Direct Legend Label Support for Contour Plots
Body: I am writing to express my concern regarding the handling of legends for contour plots in recent versions of matplotlib. While line plots (plot) allow direct assignment of legend labels via the label argument, contour plots (contour) do not support this feature. Attempts to use the label argument wi ...
Tag: 

### 53. matplotlib/matplotlib#30529  predicted **feature**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/30529
Title: Examples using Bivariate and Multivariate color maps
Body: Project https://github.com/orgs/matplotlib/projects/9, which resolves github.com/matplotlib/matplotlib/issues/14168 is divided into a number of milestones, of which this is one (highlighted in bold). * Classes for bivariate and multivariate colormaps * `Colorizer` and `ColorizingArtist` to replace ` ...
Tag: 

### 54. matplotlib/matplotlib#30623  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30623
Title: [Bug]: Line3D is not represented correctly in a plot.
Body: ### Bug summary It's pretty simple, Line3D should be represented as a cylinder not a 2D line that has a 3rd axis designation. ### Code for reproduction ```Python make a 3d plot and add a line to it then rotate around the plot you will see that the line is flat and not 3D. ``` ### Actual outcome a fl ...
Tag: 

### 55. matplotlib/matplotlib#30638  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30638
Title: Add support for specifying an initial directory for the “Save” dialog in the Matplotlib toolbar
Body: **Hi Matplotlib team, first of all, thank you for your amazing work — I use Matplotlib every day in an automated measurement environment. I’d like to propose a small improvement regarding the Save dialog behavior.** ### The Problem When saving a figure via the standard Matplotlib toolbar (the disk i ...
Tag: 

### 56. matplotlib/matplotlib#30793  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/30793
Title: [ENH]: Setting custom display range in colorbar
Body: ### Problem I have been trying to set a custom display range for the colorbar in matplotlib, but have not been able to do much. ``` # Plot: test.png plt.figure(figsize=(9, 9)) # Create a grid for contour plotting x_grid = np.linspace(dat_test['x'].min(), dat_test['x'].max(), 100) y_grid = np.linspac ...
Tag: 

### 57. matplotlib/matplotlib#31747  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/31747
Title: [MNT]: hardcoded zoom in view_init
Body: ### Summary The issue is in the `view_init` method of the `Axes3D` class in `mpl_toolkits`. `self._dist` which is explained to be the "camera distance from origin" in a comment, is hardcoded to 10, which makes it not changeable unless i edit the code. i would like to be able to zoom how i want ### P ...
Tag: 

### 58. matplotlib/matplotlib#32121  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/32121
Title: [MNT]: Please provide wheels for aarch64
Body: ### Summary Hi, seemingly pip install doesnt find wheels for aarch64. I try to install matplotlib on a raspi 4 running a restricted OS, which doesn't allow installation of additional software packages (like eg gcc, so compilation doesnt work there either). Other python packages intall fine from whee ...
Tag: 

### 59. matplotlib/matplotlib#32207  predicted **feature**, maintainers ['question']
https://github.com/matplotlib/matplotlib/issues/32207
Title: [MNT]: Figure size as defined
Body: ### Summary When I use matplotlib to create figures that are supposed to have a fixed size, they should actually be that size. This only works if you set `constrained_layout=True`. However, I think this should be the default value when `figsize=(width, height)` is set. Maybe there are good reasons w ...
Tag: 

### 60. matplotlib/matplotlib#32381  predicted **feature**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/32381
Title: [ENH]: WSL support
Body: ### Problem Actually it is not user-friendly to run Matplotlib on WSL. Moreover, this answer [python - Show matplotlib plots (and other GUI) in Ubuntu (WSL1 & WSL2) - Stack Overflow](https://stackoverflow.com/questions/43397162/show-matplotlib-plots-and-other-gui-in-ubuntu-wsl1-wsl2?answertab=scored ...
Tag: 

### 61. matplotlib/matplotlib#32409  predicted **feature**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/32409
Title: [ENH]: Expose KDE weights parameter in violinplot
Body: ### Problem I have encountered a situation where the KDE calculation in `violinplot `can be significantly improved by using precomputed weights (memory overflow crash vs several seconds). It would help me significantly (I had to write my own implementation) if it was exposed. ### Proposed solution E ...
Tag: 

### 62. numpy/numpy#31027  predicted **feature**, maintainers ['bug']
https://github.com/numpy/numpy/issues/31027
Title: BUG/ENH: `np.sinc(np.inf)` generates warning and returns `nan`
Body: The function $$\textrm{sinc}(x)$$ approaches 0 as $$x \rightarrow \infty$$ (for real $x$), so it would be nice if `np.sinc` implemented this limit. Currently `np.sinc(np.inf)` generates a runtime warning and returns `nan`: ``` In [2]: np.__version__ Out[2]: '2.5.0.dev0+git20260316.80bcb8b' In [3]: n ...
Tag: 

### 63. numpy/numpy#32136  predicted **feature**, maintainers ['bug']
https://github.com/numpy/numpy/issues/32136
Title: PERF: np.sin(a, where=) is slower than computing the whole array
Body: ### Describe the issue: The current implementation finds runs where mask = 1 and calculates on them separately. With a random mask it kills speed. The benchmark below compares 3 algorithms: 1) where = default sin(a, where=m,out=b) 2) bsl = calculate sin over the whole a and store it to the buffer. A ...
Tag: 

### 64. numpy/numpy#32453  predicted **feature**, maintainers ['bug']
https://github.com/numpy/numpy/issues/32453
Title: PERF: F->C order conversion thrashes the L3 cache
Body: ### Describe the issue: I benchmarked `b = np.ascontiguousarray(a.T)`, where `a` is a C-contiguous array, and `b[:] = a.T`, where `a` and `b` are both C-contiguous. The conversion from Fortran-order to C-order runs at ~3.9 GB/s, which is a bit slower than a plain memcpy of a C-order array at ~6 GB/s ...
Tag: 

### 65. numpy/numpy#33062  predicted **feature**, maintainers ['bug']
https://github.com/numpy/numpy/issues/33062
Title: ENH: linalg: Consider improving accuracy of 2x2 det using Kahan's algorithm
Body: ### Describe the issue: Relative forward error of numpy.linalg.det() can be catastrophically bad, even for 2x2 matrices. For the 2x2 case, it would be easy to do much much better-- maximum error <1.5 ulps can be achieved with 3 or so lines of python code. An example where it currently behaves badly ...
Tag: 

### 66. matplotlib/matplotlib#31156  predicted **question**, maintainers ['docs']
https://github.com/matplotlib/matplotlib/issues/31156
Title: Spam
Body: ### Documentation Link https://github.com/matplotlib/matplotlib/issues/31130 ### Problem You've gotten the capacity of feelings and reasoning and purpose It's not far too long before you realize, you are worthy, we are all particles flowing in space with or without yukawa coupling It would be appare ...
Tag: 

### 67. matplotlib/matplotlib#32145  predicted **question**, maintainers ['feature']
https://github.com/matplotlib/matplotlib/issues/32145
Title: [ENH]: Missing documentation (or functional) info on how to create hyperlinks to specific legend text
Body: ### Problem Looking through the issues and searching with AI, I cannot find any example on how to actually be able to click on a piece of text in the legend and have it open a url. There was an old issue (here) in #25567 but it was closed for no clear reason. And where the example and discussion was ...
Tag: 

