import os
import os.path

class Path:
	def __init__(self,s):
		assert isinstance(s,str)
		self.s = s

	def __truediv__(self,other):
		assert isinstance(other,str)
		return Path(
			os.path.join(
				self.s,
				other))

	def __repr__(self):
		return os.path.abspath(self.s).__repr__()

	def __str__(self):
		return os.path.abspath(self.s).__str__()

	def is_directory(self):
		return os.path.isdir(
			self.s)

	def mkdir_recursive(self):
		os.makedirs(
			self.s)

	def is_file(self):
		return os.path.isfile(
			self.s)

	def remove(self):
		os.remove(
			self.s)
