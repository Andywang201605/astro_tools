

#myms='../j1728-3345.ms'
myms = '../j1736-3216.ms'
imagename='../images/j1736-3216.Image.2100MHz'

imsize = 4096
iterations = 3000
cellsize = ['1.0arcsec']
clean_scales = [0, 3, 8]
pblim = 0.01
threshold = 3E-5
spw = ['1']

# IMPORT MIRIAD TO MEASUREMENT SETS

tclean(vis=myms,
       field='0',
       spw = spw,
       cell=cellsize,
       imsize=[imsize],
#        savemodel='modelcolumn',
       threshold=threshold,
       niter=iterations,
       imagename=imagename,
       nterms=2,
       deconvolver='mtmfs',
#       scales=clean_scales,
       weighting='briggs',
       robust=0,
       uvrange='>100lambda',
       stokes='I',
       pblimit=-1)

exportfits(imagename='{}.image.tt0'.format(imagename),
           fitsimage='{}.image.tt0.fits'.format(imagename)
          )
