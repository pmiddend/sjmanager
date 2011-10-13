import sjmanager.log
import sjmanager.downloader.base
import sjmanager.util
import urllib.parse
import http.cookiejar
import urllib.request
import tempfile
import time
import gzip

def _chunk_read(
	response,
	report_hook,
	output_file,
	chunk_size = 8192):

	if 'Content-Length' not in response.info():
		sjmanager.log.log("Shit, didn't get Content-Length from {} (headers were {}), reading all at once".format(
			response.geturl(),
			response.info()))

		output_file.write(
			response.read())

		return

	total_size = response.info()['Content-Length'].strip()
	total_size = int(total_size)
	bytes_so_far = 0

	while True:
		chunk = response.read(chunk_size)
		bytes_so_far += len(chunk)

		if not chunk:
			break

		output_file.write(
			chunk)

		if report_hook:
			#sjmanager.log.log(
			#	"{} bytes so far".format(bytes_so_far))

			report_hook(
				int(
					bytes_so_far * 100.0 / total_size))

class Native(sjmanager.downloader.base.Base):
	def __init__(
		self,
		config_file):
		pass

	# Note: static!
	def available(config_file):
		return True

	def touch(
		self,
		url):
		urllib.request.urlopen(url)

	def download(
		self,
		url,
		percent_callback,
		output_file_path = None,
		post_dict = None,
		cookie = None):

		assert isinstance(url,str)
		assert output_file_path == None or isinstance(output_file_path,sjmanager.util.Path)
		assert post_dict == None or isinstance(post_dict,dict)

		sjmanager.log.log('Downloading {}'.format(url))

		if output_file_path:
			# Same mode parameter as  for NamedTemporaryFile
			result = open(
				str(output_file_path),
				mode='w+b')
		else:
			result = tempfile.NamedTemporaryFile()

		urlencoded_post_dict = None
		if post_dict:
			urlencoded_post_dict = urllib.parse.urlencode(
				post_dict)

		cj = http.cookiejar.CookieJar()

		if cookie:
			#domain = urllib.parse.urlparse(
			#	url).netloc
			domain = 'rapidshare.com'

			sjmanager.log.log('Cookie: {}, Domain was {}'.format(cookie,domain))

			cj.set_cookie(
				http.cookiejar.Cookie(
					version = 0,
					name = cookie[0],
					value = cookie[1],
					port = None,
					port_specified = False,
					domain = domain,
					domain_specified = True,
					domain_initial_dot = None,
					path = '/',
					path_specified = True,
					secure = False,
					expires = time.time() + 10000,
					discard = True,
					comment = None,
					comment_url = None,
					rest = None))

		opener = urllib.request.build_opener(
			urllib.request.HTTPCookieProcessor(
				cj))

		urlencoded_bytes = bytes(urlencoded_post_dict,encoding='utf8') if urlencoded_post_dict != None else None

		try:
			response = opener.open(
				url,
				data = urlencoded_bytes)

			_chunk_read(
				response,
				report_hook = percent_callback,
				output_file = result)

			result.flush()

			if 'Content-Encoding' in response.info() and response.info()['Content-Encoding'] == 'gzip':
				sjmanager.log.log('Got compressed data, decompressing')
				result.seek(0)
				decompressed_content = gzip.decompress(
					result.read())
				result.truncate()
				result.seek(0)
				result.write(
					decompressed_content)
				result.seek(0)

		except Exception as e:
			sjmanager.log.log('Damn, got an exception: {}'.format(e))
			return None

		result.seek(0)

		# If we wanted to output the whole file (not recommended)
		#sjmanager.log.log("Download successful: {}".format(result.read().decode(encoding='utf8',errors='ignore')))

		result.seek(0)

		return result


	def track_link(
		self,
		link):
		assert isinstance(link,str)

		sjmanager.log.log('Tracking link {}'.format(link))

		return [urllib.request.urlopen(link).geturl()]
