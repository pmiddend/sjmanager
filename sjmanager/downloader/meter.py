import sys
import sjmanager.dialog

class Dialog:
	def __init__(self,title):
		assert isinstance(title,str)

		self.progress_meter = sjmanager.dialog.ProgressMeter(
			title)

	def __call__(self,percent):
		assert isinstance(percent,int)

		self.progress_meter.update(
			percent)

	def __del__(self):
		self.progress_meter.close()

class Simple:
	def __init__(self,title):
		assert isinstance(title,str)
		print(title+": ");

	def __call__(self,percent):
		sjmanager.log.log('Got {} percent (type {})'.format(percent,type(percent)))

		assert isinstance(percent,int)

		sys.stdout.write('\r|{}>{}| {}%'.format(percent * '-', (100 - 1 - percent) * ' ', percent))

		if percent == 100:
			sys.stdout.write('\n')
			sys.stdout.flush()

