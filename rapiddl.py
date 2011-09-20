#!/usr/bin/python3

import tempfile
import subprocess
import os
import os.path
import sys
import re
import sjmanager.rs
import sjmanager.curl
import sjmanager.rar
import urllib.parse

class Url:
	def __init__(self,content):
		self.content = content
		self.has_error = False

	def __repr__(self):
		return self.content.__repr__()

	def check(self):
		try:
			self.content = sjmanager.rs.make_proper_link(
				self.content)
		except Exception as message:
			self.error = "Couldn't make it a proper link: {}".format(message)
			self.has_error = True
			return

		result_code,result_string = sjmanager.rs.check_link(
			self.content)

		if result_code == sjmanager.rs.RS_CHECK_LINK_OK:
			return

		self.error = "Link checking failed: {}".format(result_string)
		self.has_error = True

class Group:
	def __init__(self,command):
		assert isinstance(
			command,
			list)

		self.command = command
		self.urls = []
		self.has_errors = False

	def append(self,url):
		self.urls.append(
			Url(
				url))

	def __repr__(self):
		return '[' + self.command.__str__() + ', ' + self.urls.__str__() + ']'

	def check(self):
		for url in self.urls:
			url.check()
			self.has_errors = self.has_errors | url.has_error

	def output(self):
		if len(self.urls) == 0:
			return ''

		result = ''

		if self.has_errors:
			result += '# There were errors in this group\n'

		result += '# {}\n'.format(' '.join(self.command))

		for url in self.urls:
			if url.has_error:
				result += '# {}\n'.format(url.error)
			if self.has_errors:
				result += '# '
			result += url.content
			result += '\n'

		return result

def main(input_file = None):
	if input_file == None:
		input_file = tempfile.NamedTemporaryFile(
			mode = 'r+',
			encoding = 'utf8')

		input_file.write(
			'# Please enter some Rapidshare URLs separated by newlines.\n')
		input_file.write(
			'# Precede with "download <path>" to have it downloaded to <path>\n\n')
		input_file.write(
			'# Precede with "extract <path> <password>" to have it extracted\n\n')
		input_file.flush()
		input_file.seek(
			0)

	if not 'EDITOR' in os.environ:
		print('Environment variable "$EDITOR" not defined, exiting...')
		sys.exit(-1);

	editor = os.environ['EDITOR']

	subprocess.call(
		[editor,input_file.name])

	input_lines = list(
		filter(
			lambda s : len(s) != 0 and s[0] != '#',
			[ s.strip() for s in input_file.readlines() ]))

	input_file.seek(0)
	input_file.truncate()

	if len(input_lines) == 0:
		print('Got no lines, exiting')
		sys.exit(-1);


	groups = []
	groups.append(
		Group(['download','.']))

	for line in input_lines:
		print(line)

		if line.startswith('extract'):
			args = re.split(
				r'\s+',
				line)

			assert len(args) >= 2, 'extract got {} arguments, expected at most 1. Arguments were: {}'.format(len(args)-1,args)

			groups.append(
				Group(
					args))
			continue

		elif line.startswith('download'):
			args = re.split(
				r'\s+',
				line)

			assert len(args) >= 2, 'download got {} arguments, expected at most 1. Arguments were: {}'.format(len(args)-1,args)
			groups.append(
				Group(
					args))
			continue
		else:
			groups[len(groups)-1].append(
				line)

	print('Groups were,',groups)

	has_errors = False
	for group in groups:
		group.check()
		if group.has_errors:
			has_errors = True

		input_file.write(
			group.output())

	input_file.flush()
	input_file.seek(0)

	if has_errors:
		return main(
			input_file)

	for group in groups:
		if len(group.urls) == 0:
			continue

		first_filename = None

		for url in group.urls:
			target_filename = os.path.basename(
				urllib.parse.urlparse(url.content).path)

			if first_filename == None:
				first_filename = target_filename

			sjmanager.rs.download(
				url = url.content,
				output_file_path = os.path.join(group.command[1],target_filename),
				percent_callback = sjmanager.curl.OutputDialog('Downloading {}'.format(
					target_filename)))

		assert first_filename != None

		if group.command[0] == 'extract':

			password_attempt = group.command[2] if len(group.command) == 3 else None

			while True:
				error = sjmanager.rar.unrar(
					first_filename,
					'Extracting {}'.format(first_filename),
					working_dir = group.command[1],
					password = password_attempt)

				if not error:
					break

				return_code,text = sjmanager.dialog.show_inputbox(
					'unraring {} returned an error: {}, continue with new password?'.format(
						first_filename,
						error))

				if return_code != sjmanager.dialog.MENU_RETURN_OK:
					print(
						"The following file couldn't be extracted: {}".format(
							first_filename))
					break

				password_attempt = text

main()
