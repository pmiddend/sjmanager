#!/usr/bin/python3

import sjmanager.config_file
import sjmanager.rar
import sjmanager.dialog
import os
import os.path

sjmanager.dialog.show_messagebox('Testing a rar file with a password, but we don\'t specify one! (We are expecting an error)')

output_dir = os.path.join(os.getcwd(),'test_rars')

error_output = sjmanager.rar.unrar(
	filename = 'part1.rar',
	title = 'Extracting part1.rar',
	working_dir = output_dir)

if error_output != None:
	sjmanager.dialog.show_messagebox('PASSED! Error was: {}'.format(error_output))
else:
	sjmanager.dialog.show_messagebox('FAILED! There was no error')

sjmanager.dialog.show_messagebox("Now we're specifying a password. Everything should work.")

error_output = sjmanager.rar.unrar(
	filename = 'part1.rar',
	title = 'Extracting part1.rar',
	password = sjmanager.config_file.config_file().get('global', 'password'),
	working_dir = output_dir)

if error_output == None:
	sjmanager.dialog.show_messagebox('PASSED! There was no error')
else:
	sjmanager.dialog.show_messagebox('FAILED! Error was: {}'.format(error_output))
