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

		assert isinstance(cookie,str)
		assert isinstance(downloader,sjmanager.downloader.base.Base)

		self.cookie = cookie
		self.downloader = downloader
	
	def from_auth_data(
		username,
		password,
		downloader):

		assert isinstance(username,str)
		assert isinstance(password,str)
		assert isinstance(downloader,sjmanager.downloader.base.Base)

		return Account(
			'no cookie',
			downloader)
	
	def make_proper_link(
		self,
		link):

		assert isinstance(link,str)

		if re.search(r'^http://(www\.)?rapidshare\.com',link):
			return link

		locations = self.downloader.track_link(
			link)

		for location in locations:
			if re.search(r'^https?://(www\.)?rapidshare\.com',location):
				return location

		raise Exception("Couldn't make '{}' to a proper RS link. The locations were {}".format(link,locations))

	def check_link(
		self,
		link):

		assert isinstance(link,str)

		def check_link_result_string(result_code):
			code_to_string = {
				CheckLink.file_not_found : 'File not found',
				CheckLink.ok : 'Ok',
				CheckLink.server_down : 'Server down',
				CheckLink.illegal : 'File marked illegal',
				CheckLink.direct_download : 'Direct download'
			}

			return code_to_string[result_code]

		assert re.match(r'https?://(www\.)?rapidshare\.com',link)

		to_check = re.sub(r'.*rapidshare\.com/files/([^\/]*)/(.*)',r'files=\1&filenames=\2',link)

		sjmanager.log.log('to_check is: '+to_check)

		check_result_file = self.downloader.download(
			url = 'http://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=checkfiles&'+to_check,
			cookie = self.cookie,
			percent_callback = lambda x : None)

		check_result = ''
		with check_result_file as f:
									check_result = str(f.read(),encoding='utf8')

		sjmanager.log.log('Check result is: '+check_result)

		result_code = int(re.sub(r'[^,]*,[^,]*,[^,]*,[^,]*,([0-9]*),.*',r'\1',check_result).strip())

		sjmanager.log.log('Result code is: '+str(result_code))

		return result_code,check_link_result_string(result_code)

	def download(
		self,
		**args):

		return self.downloader.download(
			cookie = self.cookie, 
			**args)
