### scripts for dirty image - casa script
import os
import glob

execfile('./deep_config.py')

### make directory
if not os.path.exists(imagepath):
    os.makedirs(imagepath)

### default configuration
def _checkdefault_():
    if Ldefaultconfig + Cdefaultconfig + Xdefaultconfig > 1:
        raise ValueError('Multiple default configurations are selected...')
    if Ldefaultconfig + Cdefaultconfig + Xdefaultconfig == 0:
        return False
    return True

def _threshold_():
    if threshold[-3:] == 'mJy':
        cleanthres = float(threshold[:-3])
        if cleanthres < 1.0:
            return '{:.0f}u'.format(cleanthres * 1e3)
        else:
            return '{:.0f}m'.format(cleanthres)
    else:
        raise NotImplementedError('other units are not supported...')

def _imagename_():
    if _checkdefault_():
        if Ldefaultconfig: tcleanconfig = Lconfig
        if Cdefaultconfig: tcleanconfig = Cconfig
        if Xdefaultconfig: tcleanconfig = Xconfig

        fitsname = '{}.spw{}.niter{}.{}jy.robust{}.clean'.format(
            '.'.join(myms.split('.')[:-1]),
            tcleanconfig['spw'],
            '{}k'.format(niter // 1000),
            _threshold_(),
            robust,
        )

    else:
        fitsname = '{}.spw{}.niter{}.{}jy.robust{}.clean'.format(
            '.'.join(myms.split('.')[:-1]),
            spw,
            '{}k'.format(niter // 1000),
            _threshold_(),
            robust,
        )
    return '{}/{}'.format(imagepath, fitsname)

def _deepdefault_():
    if Ldefaultconfig: tcleanconfig = Lconfig
    if Cdefaultconfig: tcleanconfig = Cconfig
    if Xdefaultconfig: tcleanconfig = Xconfig

    imagename = _imagename_()
    ### perforn cleaning
    tclean(
        vis = myms,
        datacolumn = datacolumn,
        weighting = weighting,
        robust = robust,
        niter = niter,
        imagename = imagename,
        spw = tcleanconfig['spw'],
        cell = tcleanconfig['cell'],
        imsize = tcleanconfig['imsize'],
        gain = gain,
        stokes = 'I',
        threshold = threshold,
        deconvolver = deconvolver,
        savemodel = savemodel,
        uvrange = uvrange,
    )

def _deepclean_():
    imagename = _imagename_()
    tclean(
        vis = myms,
        datacolumn = datacolumn,
        weighting = weighting,
        robust = robust,
        niter = niter,
        imagename = imagename,
        spw = spw,
        cell = cell,
        imsize = imsize,
        gain = gain,
        stokes = 'I',
        threshold = threshold,
        deconvolver = deconvolver,
        savemodel = savemodel,
        uvrange = uvrange,
    )

def _exportfits_():
    imageprefix = _imagename_()
    imageimagett0 = imageprefix + '.image.tt0'
    fitsimagett0 = imageimagett0 + '.fits'
    exportfits(
        imagename = imageimagett0,
        fitsimage = fitsimagett0,
    )

def _cleanlog_():
    os.system('rm casa-*.log')
    os.system('rm *.last')

### remove previous images ###
imagefiles = glob.glob('{}*'.format(_imagename_()))
if len(imagefiles) > 0:
    # check = input('previous files found... press `Y` to continue...')
    # if check.lower() != 'y':
    #     raise ValueError('Files already existed... Aborted')
    for file in imagefiles:
        os.system('rm -rf {}'.format(file))

######## main function to perform cleaning ########
if _checkdefault_():
    _deepdefault_()
else:
    _deepclean_()
_exportfits_()
_cleanlog_()