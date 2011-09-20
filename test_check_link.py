#!/usr/bin/python3

import sjmanager.rs
import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

downloader = sjmanager.downloader.factory.create(
	config_file)

acc = sjmanager.rs.Account(
	'enc={}'.format(
		config_file.get(
			'rs',
			'cookie')),
	downloader)

print('The following should be found')
print(acc.check_link('http://rapidshare.com/files/120667164/Amy.Ried.CFC.part1.rar'))
print('The following should NOT be found')
print(acc.check_link('http://rapidshare.com/files/120667166/Amy.Ried.CFC.part1.rar'))
print('Downloading a file')
print(acc.download(
	url = 'http://rapidshare.com/files/120667164/Amy.Ried.CFC.part1.rar',
	percent_callback = sjmanager.downloader.meter.simple).name)
