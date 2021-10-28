myms = '../j1728-3345.ms'
targets = ['j1728-3345']


clearstat()
clearstat()


for target in targets:
    flagdata(vis=myms,mode='rflag',field=target)
    flagdata(vis=myms,mode='tfcrop',field=target)
    flagdata(vis=myms,mode='extend',growtime=90.0,growfreq=90.0,growaround=True,flagneartime=True,flagnearfreq=True,field=target)


flagmanager(vis=myms,mode='save',versionname='tfcrop_targets')


clearstat()
clearstat()
