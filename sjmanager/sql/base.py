import abc

class Base(object):
	__metaclass__ = abc.ABCMeta

# not available in 3.1
#	@abc.abstractstaticmethod
	def available(
		config_file):
		""" Return a boolean indicating if the SQL module is available """
		return

	@abc.abstractmethod
	def execute(
		self,
		statement,
		*args):
		"""
		Execute "statement", return an array of associative arrays, representing the result.
		"""
		return

	@abc.abstractmethod
	def executemany(
		self,
		statement,
		*args):
		return

	@abc.abstractmethod
	def commit(
		self):
		"""
		Commit all statements
		"""
		return

	def execute_and_commit(
		self,
		statement,
		*args):
		assert isinstance(statement,str)

		self.execute(
			statement,
			*args)
		self.commit()

