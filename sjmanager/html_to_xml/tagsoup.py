import sjmanager.log
import sjmanager.util
import sjmanager.html_to_xml.base
import tempfile
import subprocess
import os

class Tagsoup(sjmanager.html_to_xml.base.Base):
	def __init__(self,config_file,xquery_processor):
		self.executable = config_file.get('tagsoup','executable',fallback = 'tagsoup')
		self.xquery_processor = xquery_processor

	def available(config_file):
		executable = config_file.get('tagsoup','executable',fallback = 'tagsoup')

		if not sjmanager.util.program_in_path(executable):
			sjmanager.log.log('tagsoup not available: {} not in path'.format(executable))
			return False

		return True

	def convert(self,f):
		"""
		f is a file object (or file-like object, is has to have ".name")
		"""
		# Has to be named since want to pass it to xqilla
		xml_output = tempfile.NamedTemporaryFile(mode='w')

		_options = ['--nons']

		xml_command = [self.executable] + _options + [f.name]

		with open(os.devnull) as devnullfile:
			subprocess.check_call(
				xml_command,
				stdout = xml_output,
				stderr = devnullfile)

		xml_output.flush()

		return xml_output
