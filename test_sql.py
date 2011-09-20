#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.sql.factory
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

sql = sjmanager.sql.factory.create(
	config_file)

print('Trying to enumerate all stored shows...')


for row in sql.execute('SELECT * FROM show'):
	print('{}: {}'.format(row['name'],row['url']))
