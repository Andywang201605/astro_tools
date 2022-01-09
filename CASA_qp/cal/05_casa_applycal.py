### apply calibrations
import os

execfile('./config.py')

if not os.path.exists('./tables/'):
    os.makedirs('./tables')

# table names

tt = myms.split('/')[-1].replace('.ms','')

ktab0 = './tables/cal_1GC_{}.K0'.format(tt)
gtab0 = './tables/cal_1GC_{}.G0'.format(tt)
bptab0 = './tables/cal_1GC_{}.B0'.format(tt)

gtab1 = './tables/cal_1GC_{}.G1'.format(tt)
ftab1 = './tables/cal_1GC_{}.F1'.format(tt)

### apply to the bpcal
applycal(
    vis = myms,
    field = bpcal,
    gaintable = [ftab1, bptab0, ktab0],
    gainfield = [bpcal, '', ''],
    parang = parang,
)

### apply to the pcal
for pcal in pcals:
    applycal(
        vis = myms,
        field = pcal,
        gaintable = [ftab1, bptab0, ktab0],
        gainfield = [pcal, '', ''],
        interp = ['nearest', '', ''],
        parang = parang,
    )

### apply to the science target
for target in targets:
    applycal(
        vis = myms,
        field = target,
        gaintable = [ftab1, bptab0, ktab0],
        gainfield = ['nearest', '', ''],
        interp = ['linear', '', ''],
        parang = parang,
    )


