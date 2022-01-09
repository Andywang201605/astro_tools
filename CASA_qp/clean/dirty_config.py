### configuration file for make dirty image

### configuration for ATCA
Ldefaultconfig = True
Cdefaultconfig = False
Xdefaultconfig = False

### parameters need to change
myms = 'xxx.ms'        # measurement set for imaging
robust = 0.5                # robust for dirty image

### parameters for imaging
spw = '0'                   # spectral window number for imaging
cell = '0.5arcsec'          # cell size for fits image
imsize = 1200               # image pixel size

### parameters not changed frequently
imagepath = './image/'      # folder path for saving images
datacolumn = 'data'
weighting = 'briggs'

##### dictionary for ATCA L/C/X clean configuration
Lconfig = {
    'spw': '0',
    'cell': '1.0arcsec',
    'imsize': 1800,
}

Cconfig = {
    'spw': '0',
    'cell': '0.2arcsec',
    'imsize': 3000,
}

Xconfig = {
    'spw': '1',
    'cell': '0.2arcsec',
    'imsize': 2000,
}
