### split target out
execfile('./config.py')

tt = myms.split('/')[-1].replace('.ms','')

for target in targets:
    opms = '{}.{}.ms'.format(tt, target)

    mstransform(
        vis = myms,
        outputvis = opms,
        field = target,
        datacolumn = 'corrected'
    )