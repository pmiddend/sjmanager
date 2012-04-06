import sjmanager.log
import sjmanager.util
import sjmanager.html_to_xml.base
import tempfile
import subprocess
import os
import re

class Tidy(sjmanager.html_to_xml.base.Base):
	def __init__(self,config_file):
		self.executable = config_file.get('tidy','executable',fallback = 'tidy')

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
		html_input = tempfile.NamedTemporaryFile('r+b')
		xml_tmp = tempfile.NamedTemporaryFile(mode='r+')
		xml_output = tempfile.NamedTemporaryFile(mode='w')

		_options = [
				'-numeric',
				'--input-encoding', 'utf8',
				'--output-encoding', 'ascii',
				'--wrap', '0',
				'--add-xml-decl', 'true',
				'--output-xml', 'true',
				'--escape-cdata', 'true',
				'--doctype', 'omit',
				'--show-warnings', 'false']
				# causes problems downstream in xquery
				#'--new-empty-tags', 'g:plusone',

		sanitized = f.read().decode('utf8')
		sanitized = re.sub(r'<g:plusone.*?>.*?</g:plusone>', '', sanitized, re.M)

		html_input.write(sanitized.encode('ascii', errors='xmlcharrefreplace'))
		html_input.flush()
		html_input.seek(0)

		xml_command = [self.executable] + _options + [html_input.name]
		sjmanager.log.log("htmltidy command line is {}".format(xml_command))

		# Can't use check_call here because warnings count as "program failed"?
		errfile = tempfile.TemporaryFile('r+')
		returncode = subprocess.call(
			xml_command,
			stdout = xml_tmp,
			stderr = errfile)
		# 0 is fine, 1 is warnings, 2 is errors, others may be added in the future,
		# who knows...
		if returncode > 1:
			errfile.seek(0)
			sjmanager.log.log(errfile.read())
			raise Exception(
				"Oh no, something went terribly wrong with tidy. See log for details.")

		xml_tmp.seek(0)
		sanitized = xml_tmp.read()
		sanitized = re.sub(r'xmlns=".*?"', '', sanitized, re.M)
		xml_output.write(sanitized)
		xml_output.flush()

		return xml_output
