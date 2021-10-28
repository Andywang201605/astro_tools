#ziteng.wang@sydney.edu.au

execfile('./config.py')

opms = myms.split('.ms')[0] + '_calibrators.ms'

field_selection = [bpcal]
for pcal in pcals:
	field_selection.append(pcal)

field_selection = ','.join(sorted(field_selection))

mstransform(vis=myms,
	outputvis=opms,
	field=field_selection,
	datacolumn='all')
