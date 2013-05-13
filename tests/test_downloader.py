#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.fsutil
import warnings
import hashlib
import configparser
import unittest

test_url_https = 'https://www.kernel.org/pub/linux/docs/lkml/reporting-bugs.html'
test_url_https_md5 = 'f738fd4cbab556532c6bcf8da1a36509'
test_url_md5 = '04e4ca70b8a2d59ed56c451c5c1d5d39'
test_url = 'http://de-mirror.org/gentoo/distfiles/3dduke13.zip'

class TestDownloader(unittest.TestCase):
		def setUp(self):
				warnings.simplefilter('ignore',category=ResourceWarning)

				self.config_file = configparser.ConfigParser()
				self.config_file.read(
						str(
								sjmanager.config_directory.config_directory() / "config.ini"))
				self.downloader = sjmanager.downloader.factory.create(
						self.config_file)

		def test_simple(self):
				result = self.downloader.download(
						url = test_url,
						percent_callback = sjmanager.downloader.meter.Null("Downloading..."))

				self.assertTrue(result)

				md5 = hashlib.md5()
				md5.update(
						result.read())

				self.assertEqual(md5.hexdigest(),test_url_md5)

		def test_dialog(self):
				#result = self.downloader.download(
				#		url = test_url,
				#		percent_callback = sjmanager.downloader.meter.Dialog('Downloading...'))

				#self.assertTrue(result)
				pass

		def test_output_file_path(self):
				output_file = sjmanager.fsutil.Path('test_file')

				result = self.downloader.download(
						url = test_url,
						output_file_path = output_file,
						percent_callback = sjmanager.downloader.meter.Null("Downloading..."))

				self.assertTrue(result)

				self.assertTrue(output_file.is_file())

				output_file.remove()

		def test_failure(self):
				result = self.downloader.download(
						url = 'http://test.com/lol',
						percent_callback = sjmanager.downloader.meter.Null("Downloading..."))

				self.assertTrue(result)

				result = self.downloader.download(
						url = 'http://llllllllllllllllllllllll.com/lol',
						percent_callback = sjmanager.downloader.meter.Null("Downloading..."))

				self.assertTrue(result)

		def test_https(self):
				result = self.downloader.download(
						url = test_url_https,
						percent_callback = sjmanager.downloader.meter.Null("Downloading..."))

				self.assertTrue(result)

				md5 = hashlib.md5()
				md5.update(
				result.read())

				self.assertEqual(md5.hexdigest(),test_url_https_md5)

if __name__ == '__main__':
		unittest.main()
