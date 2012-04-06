import sjmanager.xquery_processor.base
import sjmanager.util
import sjmanager.log
import tempfile
import subprocess
import re

class Xqilla(sjmanager.xquery_processor.base.Base):
	def available(
		config_file):
		executable = config_file.get('xqilla','executable',fallback = 'xqilla')

		if not sjmanager.util.program_in_path(executable):
			sjmanager.log.log('xqilla not available: {} not in path'.format(executable))
			return False

		return True

	def __init__(
		self,
		config_file):

		self.executable = config_file.get('xqilla','executable',fallback = 'xqilla')
		assert sjmanager.util.program_in_path(self.executable)

	def run(
		self,
		command,
		xml_file,
		clean = True):
		assert isinstance(xml_file,sjmanager.util.Path)

		with tempfile.NamedTemporaryFile(mode = 'w+') as xquery_command_file:
			xquery_tool = [self.executable,xquery_command_file.name]
			sjmanager.log.log("xqilla command line is {}".format(xquery_tool))
			xquery_command_file.write(
				command.replace(
					'<<<INPUTFILE>>>',
					str(
						xml_file)))
			xquery_command_file.flush()
			subprocess_output = str(
					subprocess.check_output(
						xquery_tool),
					encoding = 'utf8').rstrip('\n')

		# FIXME: this can't be very efficient...
		if clean:
			subprocess_output = re.sub(
				r'\n+',
				r'\n',
				subprocess_output)

			subprocess_output = [line.lstrip() for line in subprocess_output.split('\n')]

		return subprocess_output
