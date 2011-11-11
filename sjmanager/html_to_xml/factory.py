import sjmanager.html_to_xml.tidy
import sjmanager.html_to_xml.tagsoup
import sjmanager.util

def create(
	config_file):

	return sjmanager.util.abstract_factory(
		config_file,
		'html_converter',
		[sjmanager.html_to_xml.tagsoup.Tagsoup, sjmanager.html_to_xml.tidy.Tidy])
