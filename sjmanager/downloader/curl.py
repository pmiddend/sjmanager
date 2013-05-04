import sjmanager.log
import sjmanager.downloader.base
import sjmanager.util
import subprocess
import tempfile
import os
import re
import time
import sys
import functools

class _Process:
	def __init__(
		self,
		args,
		stdout_file):
		print('Initing curl')

		assert isinstance(args,list)

		self.process = subprocess.Popen(
				args,
				stdout = stdout_file,
				stderr = subprocess.PIPE,
				bufsize = 256)

		self.line_buffer = ''
		self.percentage = 0

	def finished(self):
		return self.process.poll() != None

	def returncode(self):
		return self.process.returncode

	def percent(self):
		self.line_buffer += str(
				self.process.stderr.read(4096),
				encoding='utf8')

		line_buffer_array = self.line_buffer.split(
				'\r')

		if len(line_buffer_array) <= 1:
			return self.percentage

		self.line_buffer = line_buffer_array.pop()
		current_status_line = line_buffer_array.pop().strip()

		search_regex = r'^\s*#*\s*(\d+).(\d+)%\s*$'

		# We don't always get a percentage indicator. For
		# example, we first get the column headers
		# So we have this check and not always update the
		# percentage. Only when we're able to.
		if re.search(search_regex,current_status_line):
			self.percentage = int(
					re.sub(
						search_regex,
						r'\1',
						current_status_line))

		return self.percentage

class Curl(sjmanager.downloader.base.Base):
	def __init__(
		self,
		config_file):

		self.executable = config_file.get(
			'curl',
			'executable',
			fallback = 'curl')

		assert sjmanager.util.program_in_path(
			self.executable)

	# Note: static!
	def available(
		config_file):
		"""
		Test for the neccessary capabilities. We need at least http
		support and libz, so we can use --compressed. We find that out using "curl -V", which returns the following:

		- The first line contains the curl version.
		- The second line contains the supported protocols
		- The third line contains "features" such as "libz", which we
						also need

		Since the curl module might be imported but not used, we test
		all this only under the condition that "curl" is in the path.
		"""
		sjmanager.log.log('Checking if curl is available')

		executable = config_file.get(
			'curl',
			'executable',
			fallback = 'curl')

		sjmanager.log.log('The config file told me the executable is {}'.format(executable))

		if not sjmanager.util.program_in_path(executable):
			sjmanager.log.log('curl not available: {} not in path'.format(executable))
			return False

		process = subprocess.Popen(
			[executable,'-V'],
			stdout = subprocess.PIPE,
			universal_newlines = True)

		assert process.wait() == 0, 'Calling curl -V resulted in an error!'

		lines = process.stdout.readlines()

		assert len(lines) == 3, 'Expected 3 lines of output from "curl -V", got {}'.format(lines)

		if not re.search(r'http',lines[1]):
			sjmanager.log.log("You curl apparently doesn't support http. Got the following protocols: {}".format(lines[1]))
			return False

		if not re.search(r'libz',lines[2]):
			sjmanager.log.log("You curl apparently doesn't support decompression. Got the following features: {}".format(lines[2]))
			return False

		return True

	def touch(
		self,
		url):

		assert isinstance(url,str)

		sjmanager.log.log('Touching {}'.format(url))

		# construct the curl commandline...
		# --head is important, it only does HEAD instead of a full request
		# Hopefully enough to keep the site satisfied
		cmd = [self.executable,'--compressed','-L', '-k','--head',url]

		with open(os.devnull) as devnullfile:
			subprocess.call(
				cmd,
				stdout = devnullfile,
				stderr = devnullfile)


	def download(
		self,
		url,
		percent_callback,
		output_file_path = None,
		post_dict = None,
		cookie = None):

		assert isinstance(url,str)
		assert output_file_path == None or isinstance(output_file_path,sjmanager.util.Path)
		assert post_dict == None or isinstance(post_dict,dict)

		sjmanager.log.log('Downloading {}'.format(url))

		if output_file_path:
			# Same mode parameter as  for NamedTemporaryFile
			result = open(
				str(output_file_path),
				mode='w+b')
		else:
			result = tempfile.NamedTemporaryFile()

		header_file = tempfile.NamedTemporaryFile()

		# construct the curl commandline...
		cmd = [self.executable,'--compressed','-L', '-k','-D',header_file.name,'-o', result.name,'-#']

		if post_dict:
			cmd += functools.reduce(
					lambda old,new:["-F",new] + old,
					map(
						lambda v:str(v[0])+'='+str(v[1]),
						post_dict.items()),
					[])

		if cookie:
			cmd += ['--cookie', cookie[0]+'='+cookie[1]]

		cmd.append(
			url)

		sjmanager.log.log('curl command line is {}'.format(cmd))

		curl_process = _Process(
				cmd,
				stdout_file = result)

		while not curl_process.finished():
			percent_callback(
				curl_process.percent())

		# the curlprocess ignores the last line, so we hack it in here
		percent_callback(
			100)

		if curl_process.returncode() != 0:
			sjmanager.log.log('error: curl returned '.format(curl_process.returncode()))
			return None

		if not re.search('HTTP/\d*.\d*\s+200',str(header_file.read(),encoding='utf8')):
			sjmanager.log.log("error: Didn't find 200 header")
			return None

		sjmanager.log.log("Download successful")

		return result


	def track_link(
		self,
		link):
		assert isinstance(link,str)

		sjmanager.log.log('Tracking link {}'.format(link))

		headers = str(
				subprocess.check_output(
					[self.executable,'--head','-L','-k','-s',link]),
				encoding = 'utf8')

		locations = re.findall(
				r'^Location: (.*)$',
				headers,
				re.MULTILINE)

		new_locations = []
		for location in locations:
			new_locations.append(
					location.strip())

		return new_locations
