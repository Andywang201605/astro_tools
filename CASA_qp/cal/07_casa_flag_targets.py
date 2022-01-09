### flag target data
execfile('./config.py')

clearstat()
clearstat()

tt = myms.split('/')[-1].replace('.ms','')

for target in targets:
    opms = '{}.{}.ms'.format(tt, target)

    flagdata(vis=opms,mode='rflag',field=target)
    flagdata(vis=opms,mode='tfcrop',field=target)
    flagdata(vis=opms,mode='extend',growtime=90.0,growfreq=90.0,growaround=True,flagneartime=True,flagnearfreq=True,field=target)


    flagmanager(vis=opms,mode='save',versionname='tfcrop_targets')

clearstat()
clearstat()