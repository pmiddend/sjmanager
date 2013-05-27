#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.fsutil
import sjmanager.rar
import warnings
import hashlib
import configparser
import unittest

test_rar_file_no_pw = sjmanager.fsutil.Path('test_rars')/'no_pw.rar'
test_rar_file_pw = sjmanager.fsutil.Path('test_rars')/'pw.rar'
test_working_dir = sjmanager.fsutil.Path('/tmp')
test_password = 'foobar'

class TestRar(unittest.TestCase):
		def setUp(self):
				warnings.simplefilter('ignore',category=ResourceWarning)

				self.config_file = configparser.ConfigParser()
				self.config_file.read(
						str(
								sjmanager.config_directory.config_directory() / "config.ini"))
				self.downloader = sjmanager.downloader.factory.create(
						self.config_file)

#		def test_no_pw(self):
#				error_string = sjmanager.rar.unrar(
#						filename = test_rar_file_no_pw,
#						working_dir = test_working_dir,
#						percent_callback = sjmanager.downloader.meter.Null("Extracting..."))
#
#				self.assertIsNone(error_string)

		def test_pw_working(self):
				error_string = sjmanager.rar.unrar(
						filename = test_rar_file_pw,
						working_dir = test_working_dir,
						password = test_password,
						percent_callback = sjmanager.downloader.meter.Null("Extracting..."))

				self.assertIsNone(error_string)

		def test_pw_fail(self):
				error_string = sjmanager.rar.unrar(
						filename = test_rar_file_pw,
						working_dir = test_working_dir,
						password = 'wrong_password',
						percent_callback = sjmanager.downloader.meter.Null("Extracting..."))

				self.assertTrue(len(error_string) > 0)

if __name__ == '__main__':
		unittest.main()
