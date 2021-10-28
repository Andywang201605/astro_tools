#ziteng.wang@sydney.edu.au

import datetime
import shutil
import pickle
import glob

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

dtab3 = '../tables/cal_1GC_C3431_{}.D3'.format(tt)

secondary_pickle = pickle.load(open(glob.glob('../tables/secondary_models_final*.p')[0],'rb'))
secondary_models = secondary_pickle[0]
secondary_mapping = secondary_pickle[1]



gaincal(vis=myms,
    field=bpcal,
    #uvrange=myuvrange,
    caltable=ktab0,
    refant = str(ref_ant),
    gaintype = 'K',
    solint = 'inf',
    parang=True)


# ------- G0 (primary; apply K0)


gaincal(vis=myms,
    field=bpcal,
    uvrange=myuvrange,
    caltable=gtab0,
    gaintype='G',
    solint='inf',
    calmode='p',
    minsnr=5,
    gainfield=[bpcal],
    interp = ['nearest'],
    gaintable=[ktab0])


# ------- B0 (primary; apply K0, G0)


bandpass(vis=myms,
    field=bpcal, 
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
    gainfield=[bpcal,bpcal],
    interp = ['nearest','nearest'],
    gaintable=[ktab0,gtab0])


flagdata(vis=bptab0,mode='tfcrop',datacolumn='CPARAM')
flagdata(vis=bptab0,mode='rflag',datacolumn='CPARAM')


# ------- Correct primary data with K0,B0,G0


applycal(vis=myms,
    gaintable=[ktab0,gtab0,bptab0],
#    applymode='calonly',
    field=bpcal,
#    calwt=False,
    parang=True,
    gainfield=[bpcal,bpcal,bpcal],
    interp = ['nearest','nearest','nearest'])


# ------- Flag primary on CORRECTED_DATA - MODEL_DATA


flagdata(vis=myms,
    mode='rflag',
    datacolumn='residual',
    field=bpcal)


flagdata(vis=myms,
    mode='tfcrop',
    datacolumn='residual',
    field=bpcal)


flagmanager(vis=myms,
    mode='save',
    versionname='bpcal_residual_flags')


# --------------------------------------------------------------- #
# --------------------------------------------------------------- #
# --------------------------- STAGE 1 --------------------------- #
# --------------------------------------------------------------- #
# --------------------------------------------------------------- #


# ------- K1 (primary; apply B0, G0)


gaincal(vis=myms,
    field=bpcal,
    #uvrange=myuvrange,
    caltable=ktab1,
    refant = str(ref_ant),
    gaintype = 'K',
    solint = 'inf',
    parang=True,
    gaintable=[bptab0,gtab0],
    gainfield=[bpcal,bpcal],
    interp=['nearest','nearest'])


# ------- G1 (primary; apply K1,B0)


gaincal(vis=myms,
    field=bpcal,
    uvrange=myuvrange,
    caltable=gtab1,
    gaintype='G',
    solint='inf',
    calmode='p',
    minsnr=5,
    gainfield=[bpcal,bpcal],
    interp = ['nearest','nearest'],
    gaintable=[ktab1,bptab0])


# ------- B1 (primary; apply K1, G1)


bandpass(vis=myms,
    field=bpcal,
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
    gainfield=[bpcal,bpcal],
    interp = ['nearest','nearest'],
    gaintable=[ktab1,gtab1])


flagdata(vis=bptab1,mode='tfcrop',datacolumn='CPARAM')
flagdata(vis=bptab1,mode='rflag',datacolumn='CPARAM')


# ------- Correct primary data with K1,G1,B1


applycal(vis=myms,
    gaintable=[ktab1,gtab1,bptab1],
#    applymode='calonly',
    field=bpcal,
#    calwt=False,
    parang=True,
    gainfield=[bpcal,bpcal,bpcal],
    interp = ['nearest','nearest','nearest'])


# --------------------------------------------------------------- #
# --------------------------------------------------------------- #
# --------------------------- STAGE 2 --------------------------- #
# --------------------------------------------------------------- #
# --------------------------------------------------------------- #


# ------- G2 (primary; a&p sols per scan / SPW)


gaincal(vis = myms,
    field = bpcal,
    uvrange = myuvrange,
    caltable = gtab2,
    refant = str(ref_ant),
    solint = 'inf',
    solnorm = False,
    combine = '',
    minsnr = 3,
    calmode = 'ap',
    parang = True,
    gaintable = [ktab1,gtab1,bptab1],
    gainfield = [bpcal,bpcal,bpcal],
    interp = ['nearest','nearest','nearest'],
    append = False)


# ------- Duplicate K1
# ------- Duplicate G2 (to save repetition of above step)


shutil.copytree(ktab1,ktab2)
shutil.copytree(gtab2,gtab3)


# ------- Looping over secondaries


solve_delays = []


for i in range(0,len(pcals)):


    pcal = pcals[i]
    pcal_name = pcal_names[i] # name


    for item in secondary_mapping:
        if item[0] == pcal_name:
            mod_idx = str(item[1])


    iflux = secondary_models[mod_idx]['fitFluxd']
    spidx = secondary_models[mod_idx]['spidx']
    if len(spidx) == 2:
        myspix = spidx[1] 
    elif len(spidx) == 3:
        alpha = spidx[1]        
        beta = spidx[2]
        myspix = [alpha,beta]
    # alpha = secondary_models[mod_idx]['spidx'][1]
    # beta = secondary_models[mod_idx]['spidx'][2]
    ref_freq = str(secondary_models[mod_idx]['fitRefFreq'])+'Hz'


    setjy(vis =myms,
        field = pcal,
        standard = 'manual',
        fluxdensity = [iflux,0,0,0],
        spix = myspix,
        reffreq = ref_freq,
        usescratch = True)


    # --- G2 (secondary)


    gaincal(vis = myms,
        field = pcal,
        uvrange = myuvrange,
        caltable = gtab2,     
        refant = str(ref_ant),
        minblperant = 2,
        minsnr = 3,
        solint = 'inf',
        solnorm = False,
        gaintype = 'G',
        combine = '',
        calmode = 'ap',
        parang = True,
        gaintable=[ktab1,gtab1,bptab1],
        gainfield=[bpcal,bpcal,bpcal],
        interp=['nearest','linear','linear'],
        append=True)


    # --- K2 (secondary)

    if iflux > delaycut: # Don't solve for delays on weak secondaries

        gaincal(vis= myms,
            field = pcal,
        #   uvrange = myuvrange,
            caltable = ktab1,
            refant = str(ref_ant),
        #   spw = delayspw,
            gaintype = 'K',
            solint = 'inf',
            parang = True,
            gaintable = [gtab1,bptab1,gtab2],
            gainfield = [bpcal,bpcal,pcal],
            interp = ['nearest','linear','linear','linear'],
            append = True)

        solve_delays.append(True)

    else:

        solve_delays.append(False)


# ------- Looping over secondaries


for i in range(0,len(pcals)):


    pcal = pcals[i]


    # --- Correct secondaries with K2, G1, B1, G2


    applycal(vis = myms,
        gaintable = [ktab2,gtab1,bptab1,gtab2],
#        applymode='calonly',
        field = pcal,
#        calwt = False,
        parang = True,
        gainfield = ['','',bpcal,pcal],
        interp = ['nearest','linear','linear','linear'])


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


# --------------------------------------------------------------- #
# --------------------------------------------------------------- #
# --------------------------- STAGE 3 --------------------------- #
# --------------------------------------------------------------- #
# --------------------------------------------------------------- #


gaincal(vis = myms,
    field = bpcal,
    uvrange = myuvrange,
    caltable = gtab3,
    refant = str(ref_ant),
    solint = 'inf',
    solnorm = False,
    combine = '',
    minsnr = 3,
    calmode = 'ap',
    parang = True,
    gaintable = [ktab2,gtab1,bptab1],
    gainfield = [bpcal,bpcal,bpcal],
    interp = ['nearest','nearest','nearest'],
    append = False)

### Pol Cal here! ###
polcal(vis=myms, field=bpcal, caltable=dtab3, refant=str(ref_ant), poltype='Df', solint='inf', gaintable=[ktab2,gtab1,bptab1], gainfield = [bpcal,bpcal,bpcal], interp = ['nearest','nearest','nearest'])

# ------- Duplicate K1 table


shutil.copytree(ktab1,ktab3)


# ------- Looping over secondaries


for i in range(0,len(pcals)):


    pcal = pcals[i]


    # --- G3 (secondary)


    gaincal(vis = myms,
        field = pcal,
        uvrange = myuvrange,
        caltable = gtab3,     
        refant = str(ref_ant),
        minblperant = 2,
        minsnr = 3,
        solint = 'inf',
        solnorm = False,
        gaintype = 'G',
        combine = '',
        calmode = 'ap',
        parang = True,
        gaintable=[ktab2,gtab1,bptab1],
        gainfield=[bpcal,bpcal,bpcal],
        interp=['nearest','linear','linear'],
        append=True)


    # --- K3 secondary


    if solve_delays[i]:

        gaincal(vis= myms,
            field = pcal,
        #   uvrange = myuvrange,
            caltable = ktab3,
            refant = str(ref_ant),
        #   spw = delayspw,
            gaintype = 'K',
            solint = 'inf',
            parang = True,
            gaintable = [gtab1,bptab1,gtab3],
            gainfield = [bpcal,bpcal,bpcal,pcal],
            interp = ['linear','linear','linear'],
            append = True)



# ------- Apply final tables to secondaries


for i in range(0,len(pcals)):


    pcal = pcals[i]


    # --- Correct secondaries with K3, G1, B1, G3


    applycal(vis = myms,
        gaintable = [ktab3,gtab1,bptab1,gtab3,dtab3],
#        applymode='calonly',
        field = pcal,
#        calwt = False,
        parang = True,
        gainfield = ['','',bpcal,pcal,''],
        interp = ['nearest','linear','linear','linear','linear'])


# ------- Apply final tables to targets


for i in range(0,len(targets)):


    target = targets[i]
    related_pcal = target_cal_map[i]


    # --- Correct targets with K3, G1, B1, G3


    applycal(vis=myms,
        gaintable=[ktab3,gtab1,bptab1,gtab3,dtab3],
#        applymode='calonly',
        field=target,
#        calwt=False,
        parang=True,
        gainfield=['',bpcal,bpcal,related_pcal,''],
        interp=['nearest','linear','linear','linear','linear'])


flagmanager(vis=myms,mode='save',versionname='refcal-full')
