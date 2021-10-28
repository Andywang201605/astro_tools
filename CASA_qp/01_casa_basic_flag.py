#ziteng.wang@sydney.edu.au

execfile('./config.py')

clearstat()
clearstat()

badfreqs = ['1821MHz~1824MHz','1293MHz~1298MHz']

myspw = ''
for badfreq in badfreqs:
    myspw += '*:'+badfreq+','
myspw = myspw.rstrip(',')

flagdata(vis = myms,
         mode = 'manual',
         spw = myspw)

flagdata(vis = myms,
	mode = 'clip',
	clipzeros = True)

flagdata(vis = myms,
	mode = 'clip',
	clipminmax = [0.0,100.0])


clearstat()
clearstat()


