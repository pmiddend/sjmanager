#!/usr/bin/python3

import time
import sjmanager.dialog

try:
	pm = sjmanager.dialog.ProgressMeter('Test progress meter')

	for i in range(0,11):
		pm.update(10 * i)
		time.sleep(0.1)
finally:
	pm.close()

return_value,selection = sjmanager.dialog.show_menu(
	'Choose something',
	[(1,'a'),(20,'b')],
	title = "That's the title")

if return_value != sjmanager.dialog.MenuReturn.ok:
	sjmanager.dialog.show_textbox('You chose to cancel')
else:
	sjmanager.dialog.show_textbox('You chose: {}'.format(selection))

sjmanager.dialog.show_textbox('This is a test\nfor multiple\nlines')

return_value,text_entered = sjmanager.dialog.show_inputbox('Enter something','initial text')
if return_value != sjmanager.dialog.MenuReturn.ok:
	sjmanager.dialog.show_textbox('You chose to cancel')
else:
	sjmanager.dialog.show_textbox('You chose: {}'.format(text_entered))

return_value = sjmanager.dialog.show_yesno('Choose yes or no')
if return_value == True:
	sjmanager.dialog.show_textbox('You chose: yes')
else:
	sjmanager.dialog.show_textbox('You chose: no')
