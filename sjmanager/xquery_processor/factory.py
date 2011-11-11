import sjmanager.xquery_processor.xqilla
import sjmanager.util

def create(
	config_file):

	return sjmanager.util.abstract_factory(
		config_file,
		'xquery_processor',
		[sjmanager.xquery_processor.xqilla.Xqilla])
