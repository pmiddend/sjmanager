import sjmanager.captcha.image_viewer
import sjmanager.util

def create(
	config_file):

	return sjmanager.util.abstract_factory(
		config_file,
		'captcha resolver',
		[sjmanager.captcha.image_viewer.ImageViewer])
