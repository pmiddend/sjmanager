#!/usr/bin/python3
import sjmanager.html_to_xml.factory
import sjmanager.xquery_processor.factory
import sjmanager.config_directory
import sjmanager.util
import tempfile
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

xquery = sjmanager.xquery_processor.factory.create(
	config_file)

html_converter = sjmanager.html_to_xml.factory.create(
	config_file,
	xquery)

with tempfile.NamedTemporaryFile() as f:
	conversion_string = '<html><ul><li>test</html>'
	print('Trying to convert {}'.format(conversion_string))
	f.write(bytes(conversion_string,encoding='utf8'))
	f.flush()

	xml_output = html_converter.convert(
		f)

	with open(xml_output.name,'r') as output:
		print('Result: {}'.format(output.read()))
