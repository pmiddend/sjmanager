import abc

class Base(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractstaticmethod
	def available(config_file):
		""" Return a boolean indicating if the downloader is available """
		return

	@abc.abstractmethod
	def touch(
		self,
		url):
		"""
		Just "visit" the url, don't download it, don't write the output somewhere.
		"""
		pass

	@abc.abstractmethod
	def download(
		self,
		url,
		percent_callback,
		output_file_path = None,
		post_dict = None,
		cookie = None):
		"""
		Download the "url", return a file-like object pointing
		to the resulting file. Store file in output_file_path
		if given, else store it in a named temporary file.

		post_dict is a dictionary of name=value pairs which
		are POST parameters.

		cookie is a string representing a single cookie

		percent_callback is a callable which is called
		regularly with an integer percent value indicating how
		far along the download is
		"""
		return

	@abc.abstractmethod
	def track_link(
		self,
		link):
		"""
		Tries to follow the link until no "302" Location
		headers are received. Each "hop" is put into a
		separate array element. Example:

		Call:
                        track_link(http://test.com)

		Result:
			['http://test.com','http://test.com/forwarded_here','http://test2.com/link.zip']
		"""
		return
