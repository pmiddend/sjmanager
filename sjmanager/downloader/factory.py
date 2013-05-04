import sjmanager.downloader.curl
import sjmanager.downloader.native
import sjmanager.log
import sjmanager.util

def create(
	config_file):

	return sjmanager.util.abstract_factory(
		config_file,
		'downloader',
		[sjmanager.downloader.curl.Curl, sjmanager.downloader.native.Native])
