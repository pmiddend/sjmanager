import subprocess
import re
import sjmanager.util
import sjmanager.dialog

rar_executable = None

if sjmanager.util.program_in_path('unrar'):
	rar_executable = 'unrar'
elif sjmanager.util.program_in_path('rar'):
	rar_executable = 'rar'
else:
	raise Exception('Found neither "rar" nor "unrar"')

class RarProcess:
	def __init__(self,args,working_dir):
		assert isinstance(working_dir,sjmanager.util.Path)

		self.process = subprocess.Popen(
			args,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			cwd = str(working_dir))

		self.line_buffer = ''
		self.percentage = 0

	def finished(self):
		return self.process.poll() != None

	def returncode(self):
		return self.process.returncode

	def stderr_output(self):
		return self.process.stderr.read()

	def percent(self):
		self.line_buffer += str(
			self.process.stdout.read(
				10),
			encoding='utf8')

		line_buffer_array = self.line_buffer.split(
			'\x08\x08\x08\x08')

#		print(line_buffer_array)

		if len(line_buffer_array) <= 1:
			return self.percentage

		self.line_buffer = line_buffer_array.pop()
		current_status_line = line_buffer_array.pop().strip()

		search_regex = r'\s*(\d+)%$'

		# We don't always get a percentage indicator. For
                # example, we first get the column headers
		# So we have this check and not always update the
                # percentage. Only when we're able to.
		if re.search(search_regex,current_status_line):
			replacement = re.sub(
					search_regex,
					r'\1',
					current_status_line)
			self.percentage = int(
				replacement)

		return self.percentage

def unrar(
	filename,
	title,
	working_dir,
	password = None):

	assert isinstance(filename,sjmanager.util.Path)
	assert isinstance(title,str)
	assert isinstance(working_dir,sjmanager.util.Path)

	args = [rar_executable,'x',str(filename),'-o+']

	if password != None:
		assert isinstance(password,str)
		args += ['-p{}'.format(password)]

	rar_process = RarProcess(
		args,
		working_dir)

	try:
		progress_meter = sjmanager.dialog.ProgressMeter(
			title)

		while not rar_process.finished():
#			print(rar_process.percent())
			progress_meter.update(
				rar_process.percent())
	finally:
		progress_meter.close()

	if rar_process.returncode() != 0:
		return rar_process.stderr_output()

	return None
