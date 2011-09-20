import subprocess
import tempfile
from sjmanager.log import log

_intro = ['dialog','--backtitle','sjmanager']

class MenuReturn:
	ok = 0
	no_or_cancel = 1
	help = 2
	extra = 3
	error = -1

def _execute_dialog_safely(args):
	assert len(args) > 0
	dialog_process = subprocess.Popen(args,stderr=subprocess.PIPE)
	return_value = dialog_process.wait()
	if return_value is MenuReturn.error:
		raise Exception('dialog returned an error')
	return return_value,str(dialog_process.stderr.read(),encoding='utf8')

def show_menu(headline,entries,title = None):
	def _menu_dictionary_to_arg_array(e):
		return sum(map(lambda x: [str(x[0]),str(x[1])],e),[])

	to_title_or_not_to_title = [] if title == None else ['--title',title]

	# --menu title height width menu height (or 0 to auto-adjust) ([tag,text])*
	return_value,tag = _execute_dialog_safely(_intro + to_title_or_not_to_title + ['--menu',headline,'0','0','0'] + _menu_dictionary_to_arg_array(entries))

	for key,value in entries:
		if str(key) == tag:
			return return_value,(key,value);

	return return_value,None

def show_messagebox(text):
	# --msgbox text height width (or 0 to auto-adjust)
	return _execute_dialog_safely(_intro + ['--msgbox',text,'0','0'])

def show_textbox(text):
	# --msgbox text height width (or 0 to auto-adjust)
	with tempfile.NamedTemporaryFile(mode='w+') as f:
		f.write(
			text)
		# Important
		f.flush()
		return _execute_dialog_safely(_intro + ['--textbox',f.name,'0','0'])

def show_inputbox(text,initial_text = None):
	# --inputbox text height width (or 0 to auto-adjust) [init-text]
	if initial_text:
		return _execute_dialog_safely(_intro + ['--inputbox',text,'0','0',initial_text])
	return _execute_dialog_safely(_intro + ['--inputbox',text,'0','0'])

def show_yesno(text):
	return_code, output = _execute_dialog_safely(
		_intro + ['--yesno',text,'0','0'])

	return True if return_code == MenuReturn.ok else False

class ProgressMeter:
	def __init__(self,title):
		self.title = title
		self.process_object = subprocess.Popen(
			_intro + ['--gauge',title,'0','100'],
			stdin = subprocess.PIPE,
			universal_newlines = True,
			bufsize = 1)

	def update(self,percent):
		self.process_object.stdin.write(str(percent)+'\n')
		self.process_object.stdin.flush()

	def close(self):
		self.process_object.communicate()

