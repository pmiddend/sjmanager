#!/usr/bin/python3

import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.config_directory
import sjmanager.ul
import sjmanager.dialog
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

downloader = sjmanager.downloader.factory.create(
	config_file)

ul = sjmanager.ul.Account(
	('login',config_file.get('ul','cookie')),
	downloader)

ul.download(url = 'http://ul.to/h61x7cor', output_file_path=sjmanager.util.Path("/tmp/test"), percent_callback=sjmanager.downloader.meter.simple)

print('Done')
