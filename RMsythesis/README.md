### Python scripts for performing RM-synthesis

credit: Emil Lenc

#### rmsynth.py

Script for making an RM-synthesized map from image cubes made by `wsclean`.

In order to use it, put the script where the cubes are, change `prefix` to whatever the name specified in `-name` setting in wsclean. The default setting is to search RM from -400 to 400 and the step size is 0.1. You can change this by changing `startPhi` and `dPhi`.

You will get two fits files: `peak.fits` and `val.fits`. `peak.fits` is the peak polarised intensity (taking the peak in RM space) and `val.fits` is the RM at that peak.
