#ziteng.wang@sydney.edu.au

execfile('./config.py')


clearstat()
clearstat()


flagdata(vis=myms,mode='rflag',datacolumn='data',field=bpcal)
flagdata(vis=myms,mode='tfcrop',datacolumn='data',field=bpcal)
flagdata(vis=myms,mode='extend',growtime=90.0,growfreq=90.0,growaround=True,flagneartime=True,flagnearfreq=True,field=bpcal)


for pcal in pcals:
    flagdata(vis=myms,mode='rflag',datacolumn='data',field=pcal)
    flagdata(vis=myms,mode='tfcrop',datacolumn='data',field=pcal)
    flagdata(vis=myms,mode='extend',growtime=90.0,growfreq=90.0,growaround=True,flagneartime=True,flagnearfreq=True,field=pcal)


flagmanager(vis=myms,mode='save',versionname='autoflag_cals_data')


clearstat()
clearstat()
