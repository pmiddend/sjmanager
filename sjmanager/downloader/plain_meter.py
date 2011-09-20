import sys

def output_plain(
	percent):

	assert isinstance(percent,int)

	sys.stdout.write(
		'\r|{}>{}| {}%'.format(
			percent * '-',
			(100 - 1 - percent) * ' ',
			percent))

	if percent == 100:
		sys.stdout.write('\n')
	sys.stdout.flush()
