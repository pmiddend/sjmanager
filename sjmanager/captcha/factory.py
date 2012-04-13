import sjmanager.captcha.image_viewer
import sjmanager.captcha.caca_viewer
import sjmanager.util

def create(
	config_file):

	#FIXME why the hell do I have to reorder this list to make caca the preferred option?
	return sjmanager.util.abstract_factory(
		config_file,
		'captcha_resolver',
		[
			sjmanager.captcha.caca_viewer.CacaViewer,
			sjmanager.captcha.image_viewer.ImageViewer,
		])
