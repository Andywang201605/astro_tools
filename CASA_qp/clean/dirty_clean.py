### scripts for dirty image - casa script
import os
import glob
execfile('./dirty_config.py')

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

def _imagename_():
    if _checkdefault_():
        if Ldefaultconfig: tcleanconfig = Lconfig
        if Cdefaultconfig: tcleanconfig = Cconfig
        if Xdefaultconfig: tcleanconfig = Xconfig

        fitsname = '{}.spw{}.robust{}.dirty'.format(
            '.'.join(myms.split('.')[:-1]),
            tcleanconfig['spw'],
            robust,
        )

    else:
        fitsname = '{}.spw{}.robust{}.dirty'.format(
            '.'.join(myms.split('.')[:-1]),
            spw,
            robust,
        )
        
    return '{}/{}'.format(imagepath, fitsname)

def _dirtydefault_():
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
        niter = 0,
        imagename = imagename,
        spw = tcleanconfig['spw'],
        cell = tcleanconfig['cell'],
        imsize = tcleanconfig['imsize'],
    )

def _dirtyclean_():
    imagename = _imagename_()
    tclean(
        vis = myms,
        datacolumn = datacolumn,
        weighting = weighting,
        robust = robust,
        niter = 0,
        imagename = imagename,
        spw = spw,
        cell = cell,
        imsize = imsize,
    )

def _exportfits_():
    imageprefix = _imagename_()
    imageimagett0 = imageprefix + '.image'
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
    _dirtydefault_()
else:
    _dirtyclean_()
_exportfits_()
_cleanlog_()