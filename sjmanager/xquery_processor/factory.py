import sjmanager.xquery_processor.xqilla

def create(
	config_file):
	string_to_processor = {
		'xqilla' : sjmanager.xquery_processor.xqilla.Xqilla 
	}

	if config_file.has_option('global','xquery_processor'):
		preferred_processor = config_file.get('global','xquery_processor')

		if not preferred_processor in string_to_processor:
			raise Exception(
				"The requested processor '{}' is unknown. Available processors are: {}".format(
					preferred_processor,
					list(
						string_to_processor.keys())))

		if string_to_processor[preferred_processor].available(config_file) == False:
			raise Exception(
				"The requested processor '{}' is not available".format(
					preferred_processor))

		return string_to_processor[preferred_processor](
			config_file)

	for key in string_to_processor:
		if string_to_processor[key].available(config_file) == False:
			continue

		return string_to_processor[key](
			config_file)

	raise Exception('No processor could be found (see the log for details)')
