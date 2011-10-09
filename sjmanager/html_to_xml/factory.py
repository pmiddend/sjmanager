import sjmanager.html_to_xml.tidy
import sjmanager.html_to_xml.tagsoup

def create(
	config_file,
	xquery_processor):
	"""
	Create a html->xml converter. Checks which one exists and returns an instance to
	it.
	"""
	string_to_converter = {
		'tagsoup' : sjmanager.html_to_xml.tagsoup.Tagsoup,
		'tidy' : sjmanager.html_to_xml.tidy.Tidy
	}

	if config_file.has_option('global','html_converter'):
		preferred_converter = config_file.get('global','html_converter')

		if not preferred_converter in string_to_converter:
			raise Exception(
				"The requested converter '{}' is unknown. Available html converters are: {}".format(
					preferred_converter,
					list(
						string_to_converter.keys())))

		if string_to_converter[preferred_converter].available(config_file) == False:
			raise Exception(
				"The requested converter '{}' is not available".format(
					preferred_converter))

		return string_to_converter[preferred_converter](
			config_file,
			xquery_processor)

	for s in string_to_converter:
		if string_to_converter[s].available(config_file) == False:
			continue

		return string_to_converter[s](
			config_file,
			xquery_processor)

	raise Exception('No converter could be found (see the log for details)')
