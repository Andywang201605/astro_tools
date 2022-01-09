### Perform calibrations
import json
import os

execfile('./config.py')

if not os.path.exists('./tables/'):
    os.makedirs('./tables')
else:
    os.system('rm -rf ./tables/*')

# table names

tt = myms.split('/')[-1].replace('.ms','')

ktab0 = './tables/cal_1GC_{}.K0'.format(tt)
gtab0 = './tables/cal_1GC_{}.G0'.format(tt)
bptab0 = './tables/cal_1GC_{}.B0'.format(tt)

gtab1 = './tables/cal_1GC_{}.G1'.format(tt)
ftab1 = './tables/cal_1GC_{}.F1'.format(tt)

### First Round calibration
# initial phase calibration for the bpcal
gaincal(
    vis = myms,
    caltable = gtab0,
    field = bpcal,
    refant = refant,
    gaintype = 'G',
    calmode = 'p',
    solint = 'int',
    minsnr = minsnr,
    parang = parang,
)

# delay calibration
gaincal(
    vis = myms,
    caltable = ktab0,
    field = bpcal,
    refant = refant,
    gaintype = 'K',
    solint = 'inf',
    minsnr = minsnr,
    gaintable = [gtab0],
    parang = parang,
)

# bandpass calibration - K0 and G0 on fly
bandpass(
    vis = myms,
    caltable = bptab0,
    field = bpcal,
    refant = refant,
    solint = 'inf',
    bandtype = 'B',
    minsnr = minsnr,
    minblperant = minblperant,
    gaintable = [gtab0, ktab0],
    parang = parang,
)

# final gain calibration for both bpcal and pcals
gaincal(
    vis = myms,
    caltable = gtab1,
    field = bpcal,
    solint = 'inf',
    refant = refant,
    gaintype = 'G',
    calmode = 'ap',
    solnorm = False,
    gaintable = [ktab0, bptab0],
    parang = parang,
)

for pcal in pcals:
    gaincal(
        vis = myms,
        caltable = gtab1,
        field = pcal,
        solint = 'inf',
        refant = refant,
        gaintype = 'G',
        calmode = 'ap',
        solnorm = False,
        gaintable = [ktab0, bptab0],
        append = True,
        parang = parang
    )

### todo - add polarisation calibration

### scale the amplitude gain
myscale = fluxscale(
    vis = myms,
    caltable = gtab1,
    fluxtable = ftab1,
    reference = bpcal,
    transfer = pcals,
    incremental = False
)

# with open('./tables/scale.json', 'w') as fp:
#     json.dump(myscale, fp)