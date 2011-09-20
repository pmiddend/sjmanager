#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.xquery_processor.factory
import sjmanager.util
import hashlib
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

xquery = sjmanager.xquery_processor.factory.create(
	config_file)

