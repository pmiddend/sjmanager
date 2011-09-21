import abc
import sjmanager.util

class Base(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractstaticmethod
	def available(
		config_file):
		""" Return a boolean indicating if the processor is available """
		return

	@abc.abstractmethod
	def run(
		self,
		command,
		xml_file,
		clean = True):
		"""
		command: xquery command to run
		xml_file: path to the xml file
		"""
		return

	def run_file(
		self,
		xquery_file,
		xml_file,
		clean = True):
		assert isinstance(xquery_file,sjmanager.util.Path)
		assert isinstance(xml_file,sjmanager.util.Path)

		with open(str(xquery_file), encoding='utf-8') as xquery_source_file:
			return self.run(
				xquery_source_file.read(), 
				xml_file,
				clean = clean)
