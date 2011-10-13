import sjmanager.downloader.curl
import sjmanager.downloader.native
import sjmanager.log

def create(
	config_file):
	"""
	Create a download manager. Checks which one exists and returns an instance to
	it.
	"""

	sjmanager.log.log("Trying to create a downloader")

	string_to_downloader = {
		'native' : sjmanager.downloader.native.Native,
		'curl' : sjmanager.downloader.curl.Curl
	}

	if config_file.has_option('global','downloader'):
		preferred_downloader = config_file.get('global','downloader')

		sjmanager.log.log("The config file contains a \"preferred downloader\": {}".format(preferred_downloader))

		if not preferred_downloader in string_to_downloader:
			raise Exception(
				"The requested downloader '{}' is unknown. Available downloader are: {}".format(
					preferred_downloader,
					list(
						string_to_downloader.keys())))

		if string_to_downloader[preferred_downloader].available(config_file) == False:
			raise Exception(
				"The requested preferred downloader '{}' is not available".format(
					preferred_downloader))

		sjmanager.log.log("Downloader is available, constructing it.")

		return string_to_downloader[preferred_downloader](
			config_file)

	for key in string_to_downloader:
		if string_to_downloader[key].available(config_file) == False:
			continue

		return string_to_downloader[key](
			config_file)

	raise Exception('No downloader could be found (see the log for details)')
