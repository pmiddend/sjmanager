import sjmanager.dialog

class DialogMeter:
	def __init__(self,title):
		assert isinstance(percent,str)

		self.progress_meter = dialog.ProgressMeter(
			title)

	def __call__(self,percent):
		assert isinstance(percent,int)

		self.progress_meter.update(
			percent)

	def __del__(self):
		self.progress_meter.close()
