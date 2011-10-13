#!/usr/bin/python3

import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import sjmanager.util
import hashlib
import configparser

#test_url_https = 'https://www.kernel.org/pub/linux/analysis/trace-cmd/trace-cmd-1.0.0.tar.bz2'
test_url_md5 = '04e4ca70b8a2d59ed56c451c5c1d5d39'
test_url = 'http://de-mirror.org/gentoo/distfiles/3dduke13.zip'

def _simplest_test(
	downloader):

	print('Now testing the simplest curl_plain call.')

	result = downloader.download(
		url = test_url,
		percent_callback = sjmanager.downloader.meter.simple)

	if not result:
		print('FAILED: Call failed')
		return

	md5 = hashlib.md5()
	md5.update(
		result.read())
	if md5.hexdigest() != test_url_md5:
		print("FAILED: md5 didn't match.")
		return

	print('PASSED.')

def _simplest_test_dialog(
	downloader):

	print('Now testing the simplest curl_dialog call.')

	result = downloader.download(
		url = test_url,
		percent_callback = sjmanager.downloader.meter.Dialog('Downloading...'))

	if not result:
		print('FAILED: Call failed')
		return

	print('PASSED.')

def _output_file_path(
	downloader):

	print('Now testing the output file path stuff.')

	output_file = sjmanager.util.Path('test_file')

	result = downloader.download(
		url = test_url,
		output_file_path = output_file,
		percent_callback = sjmanager.downloader.meter.simple)

	if not result:
		print('FAILED: Call failed')
		return

	if output_file.is_file():
		output_file.remove()
		print('PASSED')
	else:
		print('FAILED')

def _failure_test(
	downloader):

	print('Now testing a nonexistent file on an existing url.')

	result = downloader.download(
		url = 'http://test.com/lol',
		percent_callback = sjmanager.downloader.meter.simple)

	if result:
		print('FAILED: Didn\'t get an error')
		return

	print('PASSED')

	print('Now testing a nonexistent url')

	result = downloader.download(
		url = 'http://llllllllllllllllllllllll.com/lol',
		percent_callback = sjmanager.downloader.meter.simple)

	if result:
		print('FAILED: Didn\'t get an error')
		return

	print('PASSED')

def _https_test(
	downloader):

	print('Now testing a https link')

	result = downloader.download(
		url = test_url_https,
		percent_callback = sjmanager.downloader.meter.simple)

	if not result:
		print('FAILED: Call failed')
		return;

	md5 = hashlib.md5()
	md5.update(
		result.read())
	if md5.digest() != test_url_md5:
		print("FAILED: md5 didn't match.")
		return

	print('PASSED.')

def _track_test(downloader):
	urls = downloader.track_link(
		'http://download.serienjunkies.org/go-61a36d5fc509e54224066d0240668c507c7431a328dde12c50cce2e8f1d017bec3b5da5f1749752f9eb55128d8b88e3f4c5dc90abc6978b94a4bf77bb2d93253c6136a7f86298e17/')

	print(urls)

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

downloader = sjmanager.downloader.factory.create(
	config_file)

#_simplest_test(
#	downloader)
#_simplest_test_dialog(
#	downloader)
#_output_file_path(
#	downloader)
#_failure_test(
#	downloader)

_track_test(
	downloader)
#_https_test()


