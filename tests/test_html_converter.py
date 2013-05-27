#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.xquery_processor.factory
import sjmanager.html_to_xml.factory
import sjmanager.fsutil
import warnings
import hashlib
import configparser
import unittest
import tempfile

class TestHtmlConverter(unittest.TestCase):
		def setUp(self):
				warnings.simplefilter('ignore',category=ResourceWarning)

				self.config_file = configparser.ConfigParser()
				self.config_file.read(
						str(
								sjmanager.config_directory.config_directory() / "config.ini"))

				self.html_converter = sjmanager.html_to_xml.factory.create(
						self.config_file)

		def test_simple(self):
				with tempfile.NamedTemporaryFile() as f:
						conversion_string = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html><head></head><body><ul><li>test</li></ul></body></html>'
						f.write(bytes(conversion_string,encoding='utf8'))
						f.flush()
						f.seek(0)

						with self.html_converter.convert(f) as xml_file:
								print(xml_file.name)
								with open(xml_file.name) as output:
										result = output.read()
										print(result)
										self.assertTrue(result.startswith('<?xml'))
										self.assertTrue('<li>test</li>' in result)


if __name__ == '__main__':
		unittest.main()
