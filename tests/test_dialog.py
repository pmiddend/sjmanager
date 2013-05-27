#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.fsutil
import warnings
import hashlib
import configparser
import unittest
import time

class TestDialog(unittest.TestCase):
		def setUp(self):
				warnings.simplefilter('ignore',category=ResourceWarning)

		def test_progress_meter(self):
				try:
						pm = sjmanager.dialog.ProgressMeter('Test progress meter')

						for i in range(0,11):
								pm.update(10 * i)
								time.sleep(0.1)
				finally:
						pm.close()

		def test_menu(self):
				return_value,selection = sjmanager.dialog.show_menu(
						'Choose "b"',
						[(1,'a'),(20,'b')],
				title = "That's the title")

				self.assertEqual(return_value,sjmanager.dialog.MenuReturn.ok)
				self.assertEqual(selection,(20,'b'))

		def test_textbox(self):
				sjmanager.dialog.show_textbox('This is a test\nfor multiple\nlines')

		def test_inputbox(self):
				return_value,text_entered = sjmanager.dialog.show_inputbox('Enter "a"','initial text')

				self.assertEqual(return_value,sjmanager.dialog.MenuReturn.ok)
				self.assertEqual(text_entered,'a')

if __name__ == '__main__':
		unittest.main()
