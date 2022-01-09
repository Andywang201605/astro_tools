### set calibrator model - casa script
execfile('./config.py')

if bpcal == '1934-638':
    setjy(
        vis = myms,
        field = bpcal,
        standard='Stevens-Reynolds 2016',
        scalebychan=True,
        usescratch=True
    )
elif bpcal == '0823-500':
    ### bpcal from atca calibrator database
    bpcal_mod = (
        [12.1339,0,0,0],
        [-0.5542,-0.3904],
        '1000.0MHz'
    )

    setjy(
        vis=myms,
        field=bpcal,
        standard='manual',
        fluxdensity=bpcal_mod[0],
        spix=bpcal_mod[1],
        reffreq=bpcal_mod[2],
        scalebychan=True,
    )
else:
    raise ValueError('THIS SCRIPT IS USED FOR ATCA ONLY!!! YOU SELECT A DIFFERENT BPCAL - %s'%(bpcal))