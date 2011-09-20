import sjmanager.config_directory
import configparser
import os.path

def config_file():
	conf = configparser.ConfigParser()
	conf.read(
		str(
			sjmanager.config_directory.config_directory() / "config.ini"))
	return conf
