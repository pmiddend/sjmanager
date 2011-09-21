import sjmanager.log
import sjmanager.util
import sjmanager.html_to_xml.base
import tempfile
import subprocess
import os

class Tidy(sjmanager.html_to_xml.base.Base):
	def __init__(self,config_file,xquery_processor):
		self.executable = config_file.get('tidy','executable',fallback = 'tidy')
		self.xquery_processor = xquery_processor
	
	def available(config_file):
		executable = config_file.get('tidy','executable',fallback = 'tidy')

		if not sjmanager.util.program_in_path(executable):
			sjmanager.log.log('tidy not available: {} not in path'.format(executable))
			return False

		return True
	
	def convert(self,f):
		"""
		f is a file object (or file-like object, is has to have ".name")
		"""
		# Has to be named since want to pass it to xqilla
		xml_tmp = tempfile.NamedTemporaryFile()
		xml_output = tempfile.NamedTemporaryFile(mode='w')

		_options = [
				'-numeric',
				'--input-encoding', 'utf8',
				'--output-encoding', 'ascii',
				'--wrap', '0',
				'--add-xml-decl', 'true',
				'--output-xml', 'true',
				'--escape-cdata', 'true',
				'--doctype', 'omit']

		xml_command = [self.executable] + _options + [f.name]

		# Can't use check_call here because warnings count as "program failed"?
		with open(os.devnull) as devnullfile:
			subprocess.call(
				xml_command, 
				stdout = xml_tmp,
				stderr = devnullfile)

		xml_output.write(
				self.xquery_processor.run_file(
					sjmanager.util.Path('xqueries')/'strip_namespace.xquery', 
					sjmanager.util.Path(
						xml_tmp.name), 
					clean = False))
		xml_output.flush()

		return xml_output
