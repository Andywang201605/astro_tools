### flagging before calibration - casa script
execfile('./config.py')

clearstat()
clearstat()

flagdata(
    vis = myms,
	mode = 'clip',
	clipzeros = True
)

flagdata(
    vis = myms,
	mode = 'clip',
	clipminmax = [0.0,100.0]
)


### mannually flagging

myspw = ''
for badfreq in badfreqs:
    myspw += '*:'+badfreq+','
myspw = myspw.rstrip(',')

flagdata(
    vis = myms,
    mode = 'manual',
    spw = myspw
)

clearstat()
clearstat()