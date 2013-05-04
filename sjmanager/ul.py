import re
import sjmanager.log
import sjmanager.downloader.base

class CheckLink:
	file_not_found = 0
	ok = 1
	server_down = 2
	illegal = 3
	direct_download = 4

class Account:
	def __init__(
		self,
		cookie,
		downloader):

		assert isinstance(downloader,sjmanager.downloader.base.Base)

		self.cookie = cookie
		self.downloader = downloader
		self.valid_link_regex = r'^https?://uploaded.net/file/.*'

	def make_proper_link(
		self,
		link):

		assert isinstance(link,str)

		if re.search(self.valid_link_regex,link):
			return link

		locations = self.downloader.track_link(
			link)

		for location in locations:
			if re.search(self.valid_link_regex,location):
				return location

		raise Exception("Couldn't make '{}' to a proper RS link. The locations were {}".format(link,locations))

	def check_link(
		self,
		link):

		assert isinstance(link,str)

		locations = self.downloader.track_link(
			link)

		return re.search('/404$',locations[-1])

	def download(
		self,
		**args):

		sjmanager.log.log('uploaded: Downloading something')

		return self.downloader.download(
			cookie = self.cookie,
			**args)
