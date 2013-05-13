import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.fsutil
import sjmanager.ul
import warnings
import hashlib
import configparser
import unittest

test_link_valid_short = 'http://ul.to/h61x7cor'
test_link_valid = 'http://uploaded.net/file/h61x7cor'
test_link_md5 = 'd5ee608f0427b2c3ed07dc80cf4a0328'

class TestDownloader(unittest.TestCase):
		def setUp(self):
				warnings.simplefilter('ignore',category=ResourceWarning)

				self.config_file = configparser.ConfigParser()
				self.config_file.read(
						str(
								sjmanager.config_directory.config_directory() / "config.ini"))

				self.downloader = sjmanager.downloader.factory.create(
						self.config_file)

				self.ul = sjmanager.ul.Account(
						('login',self.config_file.get('ul','cookie')),
						self.downloader)

		def test_make_proper_link(self):
				test_link = 'http://uploaded.net/file/...'
				result = self.ul.make_proper_link(test_link)
				self.assertEqual(test_link,result)

				test_link_invalid = 'http://test.com/lol'

				with self.assertRaises(Exception):
						self.ul.make_proper_link(test_link_invalid)

				result = self.ul.make_proper_link(test_link_valid_short)

				self.assertEqual(result,test_link_valid)


		def test_download(self):
				result = self.ul.download(
						url = test_link_valid,
						percent_callback = sjmanager.downloader.meter.Null("Downloading..."))

				md5 = hashlib.md5()
				md5.update(
						result.read())

				self.assertEqual(md5.hexdigest(),test_link_md5)

if __name__ == '__main__':
		unittest.main()
