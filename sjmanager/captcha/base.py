import abc

class Base(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractstaticmethod
	def available(
			config_file):
		""" Return a boolean indicating if the captcha resolver is available """
		return

	@abc.abstractmethod
	def resolve(
			self,
			image_file):
		"""
		Display image (somehow, maybe convert before that), return the containing text
		"""
		return
