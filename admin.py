#!/usr/bin/python3
import sjmanager.dialog
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import re
import configparser
import sjmanager.config_directory

config_file_name = str(
		sjmanager.config_directory.config_directory() / "config.ini")

config_file = configparser.ConfigParser()
config_file.read(
	config_file_name)

downloader = sjmanager.downloader.factory.create(
	config_file)

return_code,user_id = sjmanager.dialog.show_inputbox('Enter your Rapidshare user id:')
if return_code != sjmanager.dialog.MenuReturn.ok:
	exit()

return_code,password = sjmanager.dialog.show_passwordbox('Enter your Rapidshare password:')
if return_code != sjmanager.dialog.MenuReturn.ok:
	exit()

result_file = downloader.download(
	url = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=getaccountdetails&login='+user_id+'&password='+password+'&withcookie=1',
	percent_callback = sjmanager.downloader.meter.Dialog(
		'Retrieving cookie'))

result = result_file.read().decode(encoding='utf8',errors='ignore')
cookie_result = re.search(r'cookie=(\w+)',result)

if cookie_result == None:
	sjmanager.dialog.show_messagebox(
		"Something didn't check out, got back: "+result)
	exit()

cookie = cookie_result.group(1)
config_file['rs']['cookie'] = cookie

with open(config_file_name,'w') as f:
	config_file.write(
		f)

sjmanager.dialog.show_messagebox(
	"Successfully wrote the new config file")
