#ziteng.wang@sydney.edu.au

import datetime
import shutil
import pickle

execfile('./config.py')

def stamp():
    now = str(datetime.datetime.now()).replace(' ','-').replace(':','-').split('.')[0]
    return now

def getfieldid(myms,field):
    tb.open(myms.rstrip('/')+'/FIELD')
    names = tb.getcol('NAME').tolist()
    for i in range(0,len(names)):
        if names[i] == field:
            idx = i
    return idx

tt = stamp()

ktab0 = '../tables/cal_1GC_C3431_{}.K0'.format(tt)
gtab0 = '../tables/cal_1GC_C3431_{}.G0'.format(tt)
bptab0 = '../tables/cal_1GC_C3431_{}.B0'.format(tt)

ktab1 = '../tables/cal_1GC_C3431_{}.K1'.format(tt)
gtab1 = '../tables/cal_1GC_C3431_{}.G1'.format(tt)
bptab1 = '../tables/cal_1GC_C3431_{}.B1'.format(tt)

ktab2 = '../tables/cal_1GC_C3431_{}.K2'.format(tt)
gtab2 = '../tables/cal_1GC_C3431_{}.G2'.format(tt)
ftab2 = '../tables/cal_1GC_C3431_{}.F2'.format(tt)

ktab3 = '../tables/cal_1GC_C3431_{}.K3'.format(tt)
gtab3 = '../tables/cal_1GC_C3431_{}.G3'.format(tt)
ftab3 = '../tables/cal_1GC_C3431_{}.F3'.format(tt)

interim_pickle = '../tables/secondary_models_interim_'+tt+'.p'
secondary_pickle = '../tables/secondary_models_final_'+tt+'.p'

### Initial calibration
gaincal(vis=myms,
    field=bpcal_name,
    uvrange=myuvrange,
    caltable=gtab0,
    gaintype='G',
    solint='inf',
    calmode='p',
    minsnr=5)

bandpass(vis=myms,
    field=bpcal_name, 
    uvrange=myuvrange,
    caltable=bptab0,
    refant = str(ref_ant),
    solint='inf',
    combine='',
    solnorm=False,
    minblperant=2,
    minsnr=3.0,
    bandtype='B',
    fillgaps=gapfill,
    parang=True,
    gainfield=[bpcal_name],
    interp = ['nearest'],
    gaintable=[gtab0])


applycal(vis=myms,
    gaintable=[gtab0,bptab0],
    field=bpcal_name,
    parang=True,
    gainfield=[bpcal_name,bpcal_name],
    interp = ['nearest','nearest'])

### Flag data
flagdata(vis=myms,
    mode='rflag',
    datacolumn='residual',
    field=bpcal_name)


flagdata(vis=myms,
    mode='tfcrop',
    datacolumn='residual',
    field=bpcal_name)


flagmanager(vis=myms,
    mode='save',
    versionname='bpcal_residual_flags')


### First Round calibration
gaincal(vis=myms,
    field=bpcal_name,
    uvrange=myuvrange,
    caltable=gtab1,
    gaintype='G',
    solint='inf',
    calmode='p',
    minsnr=5,
    gainfield=[bpcal_name],
    interp = ['nearest'],
    gaintable=[bptab0])

bandpass(vis=myms,
    field=bpcal_name,
    uvrange=myuvrange,
    caltable=bptab1,
    refant = str(ref_ant),
    solint='inf',
    combine='',
    solnorm=False,
    minblperant=2,
    minsnr=3.0,
    bandtype='B',
    fillgaps=gapfill,
    parang=True,
    gainfield=[bpcal_name],
    interp = ['nearest'],
    gaintable=[gtab1])

applycal(vis=myms,
    gaintable=[gtab1,bptab1],
    field=bpcal_name,
    parang=True,
    gainfield=[bpcal_name,bpcal_name],
    interp = ['nearest','nearest'])

### Second Round Calibration
gaincal(vis = myms,
    field = bpcal_name,
    uvrange = myuvrange,
    caltable = gtab2,
    refant = str(ref_ant),
    solint = 'inf',
    solnorm = False,
    combine = '',
    minsnr = 3,
    calmode = 'ap',
    parang = True,
    gaintable = [gtab1,bptab1],
    gainfield = [bpcal_name,bpcal_name],
    interp = ['nearest','nearest'],
    append = False)

shutil.copytree(gtab2,gtab3)

# Loop over secondaries
for i in range(0,len(pcal_names)):
    pcal = pcal_names[i]

    gaincal(vis = myms,
        field = pcal,
        uvrange = myuvrange,
        caltable = gtab2,     
        refant = str(ref_ant),
        smodel = [1,0,0,0],
        minblperant = 2,
        minsnr = 3,
        solint = 'inf',
        solnorm = False,
        gaintype = 'G',
        combine = '',
        calmode = 'ap',
        parang = True,
        gaintable=[gtab1,bptab1],
        gainfield=[bpcal_name,bpcal_name],
        interp=['linear','linear'],
        append=True)

secondary_models = fluxscale(vis=myms,
    caltable = gtab2,
    fluxtable = ftab2,
    reference = bpcal_name,
    append = False,
    transfer = '')

secondary_mapping = [] # To link field names to IDs in model dict, as different from master MS


for i in range(0,len(pcal_names)):


    pcal = pcal_names[i] # Using field names
    pcal_idx = getfieldid(myms,pcal)
    secondary_mapping.append((pcal,pcal_idx))


    # --- Correct secondaries with G1, B1, F2


    applycal(vis = myms,
        gaintable = [gtab1,bptab1,ftab2],
        field = pcal,
        calwt = False,
        parang = True,
        gainfield = [bpcal_name,bpcal_name,pcal],
        interp = ['nearest','nearest','linear'])


    # --- Predict model data from fitted secondary models


    iflux = secondary_models[str(pcal_idx)]['fitFluxd']
    spidx = secondary_models[str(pcal_idx)]['spidx']
    if len(spidx) == 2:
        myspix = spidx[1] 
    elif len(spidx) == 3:
        alpha = spidx[1]        
        beta = spidx[2]
        myspix = [alpha,beta]
    ref_freq = str(secondary_models[str(pcal_idx)]['fitRefFreq'])+'Hz'


    setjy(vis =myms,
        field = pcal,
        standard = 'manual',
        fluxdensity = [iflux,0,0,0],
        spix = myspix,
        reffreq = ref_freq,
        usescratch = True)


    # --- Flag secondaries on CORRECTED_DATA - MODEL_DATA


    flagdata(vis = myms,
        field = pcal,
        mode = 'rflag',
        datacolumn = 'residual')


    flagdata(vis = myms,
        field = pcal,
        mode = 'tfcrop',
        datacolumn = 'residual')


flagmanager(vis=myms,mode='save',versionname='pcal_residual_flags')

pickle.dump((secondary_models,secondary_mapping),open(interim_pickle,'wb'))

### Third Round Calibration
for i in range(0,len(pcal_names)):


    pcal = pcal_names[i] # Using field names
    pcal_idx = getfieldid(myms,pcal)


    # --- G3 (secondary)


    gaincal(vis = myms,
        field = pcal,
        uvrange = myuvrange,
        caltable = gtab3,     
        refant = str(ref_ant),
        minblperant = 2,
        smodel=[1,0,0,0],
        minsnr = 3,
        solint = 'inf',
        solnorm = False,
        gaintype = 'G',
        combine = '',
        calmode = 'ap',
        parang = True,
        gaintable=[gtab1,bptab1],
        gainfield=[bpcal_name,bpcal_name],
        interp=['nearest','nearest'],
        append=True)



# ------- F3


secondary_models_final = fluxscale(vis=myms,
    caltable = gtab3,
    fluxtable = ftab3,
    reference = bpcal_name,
    append = False,
    transfer = '')


pickle.dump((secondary_models_final,secondary_mapping),open(secondary_pickle,'wb'))




