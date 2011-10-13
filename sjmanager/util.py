import os
import os.path
import sjmanager.log

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

def program_in_path(program):
	"""
	Returns (absolute) path of program if it is in $PATH,
	otherwise None.
	If multiple instances are found, take the first one (by
	occurrence in $PATH variable).
	"""
	assert type(program) == str
	results = list(filter(
			os.path.exists,
			[
				os.path.join(path, program) 
				for path in os.environ['PATH'].split(
					os.path.pathsep)
			]))
	if results:
		return results[0]
	return None

def strip_prefix_suffix(strings, case_sensitive = True):
	def prefix(strings):
		shortest = min(strings, key=len)
		for idx in range(1, len(shortest) + 1):
			for s in strings:
				if not s.startswith(shortest[:idx]):
					return idx - 1
		return len(shortest)

	def suffix(strings):
		shortest = min(strings, key=len)
		for idx in range(len(shortest) + 1, -1, -1):
			for s in strings:
				if not s.endswith(shortest[idx:]):
					return len(shortest) - (idx + 1)
		return len(shortest)

	if case_sensitive:
		strings = [s.lower() for s in strings]

	left, right = prefix(strings), suffix(strings)
	return [string[left:len(string)-right] for string in strings]

def abstract_factory(
	config_file,
	description,
	class_list):

	if config_file.has_option('global',description):
		preferred_class = config_file.get('global',description)

		sjmanager.log.log("The config file contains a \"preferred {}\": {}".format(description,preferred_class))

		for c in class_list:
			if c.__name__ != preferred_class.capitalize():
				continue

			sjmanager.log.log("Found it in the class list!")

			if c.available(config_file) == False:
				raise Exception(
					"The requested preferred {} '{}' is not available".format(
						description,
						preferred_class))

			sjmanager.log.log("{} {} is available, constructing it.".format(description,preferred_class))

			return c(
				config_file)

	for c in class_list:
		sjmanager.log.log('Testing {} {} for availability...'.format(description,c.__name__))
		if c.available(config_file):
			sjmanager.log.log("It's available!...")
			return c(
				config_file)

	raise Exception('No {} could be found (see the log for details)'.format(description))
