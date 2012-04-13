import sjmanager.captcha.base
import sjmanager.util
import sjmanager.log
import sjmanager.dialog
import subprocess

class ImageViewer(sjmanager.captcha.base.Base):
	def __init__(
			self,
			config_file):
		self.program = 'feh'

		if not sjmanager.util.program_in_path(self.program):
			self.program = 'display'

		sjmanager.log.log('Chose {} as captcha resolve image viewer'.format(self.program))

	def available(
			config_file):
		return sjmanager.util.program_in_path('feh') or sjmanager.util.program_in_path('display')

	def resolve(
			self,
			image_file_name):
		assert isinstance(image_file_name,sjmanager.util.Path)

		subprocess.check_call([self.program,str(image_file_name)])

		return_code,text = sjmanager.dialog.show_inputbox('What was the captcha text?')
		if return_code != sjmanager.dialog.MenuReturn.ok:
			return None
		return text
