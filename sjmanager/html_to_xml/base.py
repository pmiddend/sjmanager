import abc

class Base(object):
	__metaclass__ = abc.ABCMeta

#	Not available in 3.1
#	@abc.abstractstaticmethod
	def available(config_file):
		""" Return a boolean indicating if the html to xml converter is available """
		return

	@abc.abstractmethod
	def convert(
		self,
		f):
		"""
		Convert the HTML file "f" to a valid XML file. Returns a named temporary
		file
		"""
		return
