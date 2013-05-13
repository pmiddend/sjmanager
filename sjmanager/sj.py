import sjmanager.downloader.base
import sjmanager.downloader.meter
import sjmanager.xquery_processor.base
import sjmanager.sql.base
import sjmanager.captcha.base
import sjmanager.dialog
import sjmanager.html_to_xml.base
import sjmanager.log
import sjmanager.fsutil
import subprocess
import hashlib
import sys
import re
import functools

# The whole structure is a bit convoluted, so I'm going to explain this
# extensively.
#
#
# API (what a user needs):
#
#
#
# The class "Sj" is the mother class. It...
#
# - manages the show caches (last watched and downloaded)
# - can produce Show objects
# - (only currently) resolves captchas
#
# To either continue a show or start watching a new show, you need a Show
# object. You can retrieve it by calling the "find_shows" method. This method
# returns an array of show objects. Don't worry, show objects are not heavy to
# construct.
#
# A show has, by definition, a set of _seasons_. Each season has a _title_ like
# "Season 1" or "Staffel 2".  Since we want to treat certain seasons the same
# way although they have a different title, we need the concept of a "mangled
# season title".
#
# You can ask a Show object for a set of mangled season titles.
#
# Using a mangled season title, you can ask a Show object for a list of Season
# objects with that title. A season object contains all the information
# specific to a season, like duration, size and so on.
#
# Each season has a set of episodes. Each episode has a title, but again, we
# want to coalesce certain episodes by their title. So again, we have the
# notion of a mangled title. You can ask a season for a set of mangled episode
# titles.
#
# You can use the mangled episode title to retrieve an Episode object. This
# episode object knows its title and its link.
#
#
# Technical information (what a developer needs):
#
# That's it for the interface. The _implementation_ has to tackle some
# difficulties. I'll start by explaining what a Show object contains. 
#
# A show object has a _URL_. With this URL, you can retrieve a list of pairs
#
# (nonmangled_season_title,season_link)
#
# This way, you can construct a list of mangled season titles. 
#
# Now, we could just follow every season link and start constructing our
# seasons, but that would be pretty expensive. So, we only construct a season
# when the user requests a set of seasons using a mangled season title.
#
# There's another problem: A single season link leads to many concrete seasons
# (called "posts"). So to construct the list of seasons with title 't', we
# follow each season link belonging to that (mangled) title and retrieve a list
# of posts.
#
# So in summation, a title results in a list of seasons, and the list of
# seasons results in a list of posts. The user, however, only has the
# association: season title -> Season object
class Sj:
	def __init__(
		self,
		config_file,
		sql,
		downloader,
		html_converter,
		xquery_processor,
		captcha,
		percent_callback_creator):

		assert isinstance(sql,sjmanager.sql.base.Base)
		assert isinstance(downloader,sjmanager.downloader.base.Base)
		assert isinstance(html_converter,sjmanager.html_to_xml.base.Base)
		assert isinstance(xquery_processor,sjmanager.xquery_processor.base.Base)
		assert isinstance(captcha,sjmanager.captcha.base.Base)

		self.config_file = config_file
		self.sql = sql
		self.downloader = downloader
		self.html_converter = html_converter
		self.xquery_processor = xquery_processor
		self.captcha = captcha
		self.show_url_to_show = {}
		self.site = self.config_file.get('global', 'site')
		# Initial touch
#		self.downloader.download(url = 'http://{}'.format(self.site),percent_callback = lambda x : None)
		self.downloader.touch(
			url = 'http://{}'.format(self.site))
		self.percent_callback_creator = percent_callback_creator

	def shows_in_watch_cache(
		self):
		"""
		Returns true if there are shows in the watch cache, false otherwise.
		"""
		return self.sql.execute('SELECT COUNT(*) c FROM last_watched').fetchone()['c'] > 0

	def video_file_name(
		self,
		show_url,
		season_title,
		episode_title):
		"""
		Given a url, a mangled season  title and a mangled episode title, return
		a filename
		"""
		return hashlib.sha1(bytes(show_url+season_title+episode_title,encoding='utf8')).hexdigest()

	def resolve_linklist(
		self,
		episode_link):
		"""
		Gets an episode link, returns a list of download links
		"""

		assert isinstance(episode_link,str)

		link_list_xquery = 'data(doc("<<<INPUTFILE>>>")//form[contains(@action, "http://download.{}/")]/@action)'.format(self.site)

		captcha_url = ''
		form_name = ''

		# This is more complex than you'd originally think. The problem
		# is that we _might_ get a captcha, but maybe we get the page
		# with the linklist directly! So first, download and parse the episode link...
		with self.html_converter.convert(self.downloader.download(url = episode_link,percent_callback = self.percent_callback_creator('Downloading captcha html file'))) as original_xmlfile:

			# ...now try to extract the captcha url and the form
			# name. If this fails, captcha_url will be an empty string
			captcha_url = self.xquery_processor.run(
				'data(doc("<<<INPUTFILE>>>")//*[@id="postit"]//img[1]/@src)',
				sjmanager.fsutil.Path(
					original_xmlfile.name))[0]
			form_name = self.xquery_processor.run(
				'data(doc("<<<INPUTFILE>>>")//input[@name="s"]/@value)',
				sjmanager.fsutil.Path(
					original_xmlfile.name))[0]

			# If it's not an empty string, we have a captcha url...
			if captcha_url != '':
				# ...so download the captcha image and resolve its text.
				captcha_code = ''
				with self.downloader.download(url = 'http://download.{}{}'.format(self.site, captcha_url), percent_callback = self.percent_callback_creator('Downloading captcha image')) as captcha_image_file:
					captcha_code = self.captcha.resolve(
						sjmanager.fsutil.Path(
							captcha_image_file.name))

					# This is a special case: We have to differentiate between "wrong
					# captcha" and, for example, user signaled he wants to go back
					if captcha_code == None:
						return None

				# Then, send the resolved text to the main page and _then_ receive the file with the link list
				post_dict = {
					's' : form_name,
					'c' : captcha_code,
					'action' : 'Download'
				}

				link_list_string = ''

				with self.downloader.download(url = episode_link,post_dict = post_dict,percent_callback = self.percent_callback_creator('Downloading linklist')) as response_html_file:
					#sjmanager.log.log('got the html file '+str(response_html_file.read(),encoding='utf8'))
					response_html_file.seek(0)
					response_xml_file = self.html_converter.convert(response_html_file)
					# Finally, extract the links
					link_list_string = self.xquery_processor.run(
						link_list_xquery,
						sjmanager.fsutil.Path(
							response_xml_file.name))

				result = link_list_string

				if len(result) == 1 and result[0] == '':
					return []

				return result
			else:
				# If we didn't get a captcha url, try to extract the links directly
				link_list_string = self.xquery_processor.run(
					link_list_xquery,
					sjmanager.fsutil.Path(
						original_xmlfile.name))

				result = link_list_string

				if len(result) == 1 and result[0] == '':
					return []

				return result

	def find_shows(
		self,
		name = None,
		url = None):
		"""
		Find a list of show objects by name or url. At least one
		of the columns has to be given, but globs are allowed

		Returns [Show]
		"""

		def dictionary_to_sql_where(d):
			return ' AND '.join(list(map(lambda v: v+" LIKE :"+v,d)))

		assert name == None or isinstance(name,str)
		assert url == None or isinstance(url,str)
		assert (name != None or url != None)

		self.__update_show_cache()

		where_dict = {}

		if name != None:
			where_dict['name'] = '%'+name+'%'
		if url != None:
			where_dict['url'] = url

		result_rows = self.sql.execute(
				'SELECT name,url FROM show WHERE ' +
					dictionary_to_sql_where(
						where_dict),
				where_dict)

		result_shows = []
		for row in result_rows:
			if not row['url'] in self.show_url_to_show:
				self.show_url_to_show[row['url']] = Show(
						self.config_file,
						self.sql,
						self.downloader,
						self.html_converter,
						self.xquery_processor,
						row['name'],
						row['url'],
						self.percent_callback_creator)
			result_shows.append(
				self.show_url_to_show[row['url']])

		sjmanager.log.log("Got {} shows".format(len(result_shows)))

		return result_shows

	def __update_show_cache(
		self):
		"""
		Load the list of all shows, store it in the
		database.

		Return nothing
		"""
		# First, check if we have to get the show list from the page
		# or if we have it cached in the database
		count_result = self.sql.execute('SELECT COUNT(*) FROM show')

		if count_result.fetchone()[0] != 0:
			return

		with self.html_converter.convert(self.downloader.download(url = 'http://{}/?cat=0&showall'.format(self.site), percent_callback = self.percent_callback_creator('Downloading show list'))) as xmlfile:
			xquery_output = self.xquery_processor.run(
					'''let $endl := "&#10;" for $entry in doc("<<<INPUTFILE>>>")//*[@id="sidebar"]/ul/li/a
								return ($entry/text(), $endl, data($entry/@href), $endl)''',
					sjmanager.fsutil.Path(
						xmlfile.name))
			l = xquery_output
			assert len(l) % 2 == 0
			show_array = functools.reduce(
				lambda old,x: old + [(l[x],l[x+1])],
				range(
					0,
					len(l),
					2),
				[])

			self.sql.executemany(
					'INSERT INTO show (name,url) VALUES (?,?)',
					show_array)
			self.sql.commit()

class Show:
	def __init__(
		self,
		config_file,
		sql,
		downloader,
		html_converter,
		xquery_processor,
		name,
		url,
		percent_callback_creator):
		"""
		This shouldn't do anything heavy, since find_shows returns a list of
		constructed show objects and this list might be large.
		"""
		assert isinstance(sql,sjmanager.sql.base.Base)
		assert isinstance(downloader,sjmanager.downloader.base.Base)
		assert isinstance(html_converter,sjmanager.html_to_xml.base.Base)
		assert isinstance(xquery_processor,sjmanager.xquery_processor.base.Base)

		self.url = url
		self.name = name
		self.config_file = config_file
		self.sql = sql
		self.downloader = downloader
		self.html_converter = html_converter
		self.xquery_processor = xquery_processor
		self.site = self.config_file.get('global', 'site')
		# The season cache is a dictionary. It maps a mangled season title to a
		# list of SeasonCacheEntry objects (see below)
		self.season_title_to_links = None
		self.percent_callback_creator = percent_callback_creator


	def episode_in_cache(
		self,
		season_title,
		episode_title):
		return self.sql.execute(
			'SELECT COUNT(*) c FROM downloaded WHERE show_url = ? AND season_title = ? AND episode_title = ?',
			(self.url,season_title,episode_title)).fetchone()['c'] > 0

	def determine_next_episode(
		self):
		"""
		Determines the next episode to watch for this show (assuming the show is in
		the watch cache)

		Returns a dictionary containing the episode title (which can be None) and
		the season title (which can be None)
		"""

		result = dict()

		sjmanager.log.log('Trying to determine next show to watch')

		# First up, check which season and which episode is in the watch cache.
		row = self.sql.execute("""SELECT 
			season_title,
			episode_title,
			finished 
			FROM last_watched 
			WHERE show_url = ?""",
			(self.url,)).fetchone()

		sjmanager.log.log("Fetched the following row: {}, {}, {}, {}".format(row['season_title'],row['episode_title'],row['finished'],row['finished'] == str(0)))

		# If it's not finished, this means there's a cache file lying around, so
		# return episode and season title so we can find it.
		if str(row['finished']) == '0':
			sjmanager.log.log("Previous show isn't finished, so taking that as new show")

			result['season_title'] = row['season_title']
			result['episode_title'] = row['episode_title']

			return result

		sjmanager.log.log(
			'Ok, season title is {}, episode title is {}'.format(
				row['season_title'],
				row['episode_title']))

		# Otherwise, if the episode title isn't numeric, there's no chance to know
		# which episode (or even season) is next. So we return nothing
		if not row['episode_title'].isnumeric():
			sjmanager.log.log('The episode title is not numeric, so returning nothing')
			result['season_title'] = None
			result['episode_title'] = None
			return result

		# If the episode title _is_ numeric, there's two cases that can happen:
		#
		# 1. There's an episode in the current season with a number one higher than
		#    the current episode
		# 2. No episode with a higher number exists. In that case, maybe we have
		#    another season to continue to
		sjmanager.log.log('Cool, the episode title is numeric')

		seasons = self.seasons(
			row['season_title'])

		# Get all the mangled episode titles in the season
		episode_titles = set()
		for season in seasons:
			episode_titles = episode_titles.union(
				season.episode_titles())

		if str(int(row['episode_title']) + 1) in episode_titles:
			sjmanager.log.log(
				"Cool, we've got an episode called {}, continuing with that".format(
					int(row['episode_title']) + 1))

			result['season_title'] = row['season_title']
			result['episode_title'] = str(int(row['episode_title']) + 1)
			return result

		sjmanager.log.log(
			"No higher episode found, checking if season is numeric")

		if not row['season_title'].isnumeric():
			sjmanager.log.log(
				"Season is not numeric, returning nothing")
			result['season_title'] = None
			result['episode_title'] = None
			return result

		sjmanager.log.log(
			"Season is numeric, checking if a higher season exists")

		titles = self.season_titles()

		if not str(int(row['season_title'])+1) in titles:
			sjmanager.log.log(
				"No higher season exists, returning nothing")
			result['season_title'] = None
			result['episode_title'] = None
			return result

		sjmanager.log.log(
			"A higher season exists, returning this season but no episode")
		result['season_title'] = str(int(row['season_title'])+1)
		result['episode_title'] = None
		return result


	def season_titles(self):
		""" 
		Returns a set of mangled season titles (strings).
		"""
		self.__update_season_title_to_links()
		return set(self.season_title_to_links.keys())

	def seasons(self,title):
		""" 
		Returns a list of seasons with the specified mangled title. This is the function that resolves the association:

		season title -> [season link] -> [post]

		to

		season title -> [season]
		"""
		self.__update_season_instances(
			title)

		result = []
		for cache_entry in self.season_title_to_links[title]:
			for post in cache_entry.seasons:
				result.append(
					post)

		return result

	def __mangle_season_title(self,title):
		assert isinstance(title,str)

		search_result = re.search(
			r'(Season|Staffel)\s+(\d+)',
			title)

		if not search_result:
			return title

		return str(int(search_result.group(2)))

	# This is used by the Show class to dismiss links that don't contain
	# "Staffel" or "Season"
	def __valid_season_title(self,title_and_link):
		pattern = re.compile(r'(Season|Staffel)\s+\d+\s*[-–-]\s*\d+')
		return not re.search(
			pattern, 
			title_and_link[0])
	
	def __update_season_instances(
		self,
		title):
		self.__update_season_title_to_links()

		for cache_entry in self.season_title_to_links[title]:
			cache_entry.follow_link(
				self.html_converter,
				self.downloader,
				self.xquery_processor)
	
	def __update_season_title_to_links(self):
		if self.season_title_to_links != None:
			return
		# Download the show url and extract the season links (with the season title)
		# Then, mangle the title and create a dict which maps from the mangled
		# title to the url
		html_file = self.downloader.download(
			url = self.url,
			percent_callback = self.percent_callback_creator('Downloading season links for season'))

		xquery_output = ''

		with self.html_converter.convert(html_file) as xmlfile:
			xquery_output = self.xquery_processor.run(
					'''let $endl := "&#10;" for $staffel in doc("<<<INPUTFILE>>>")//div[@id="scb"]//a[contains(@href,"{}")]
					return ( $staffel/text(), $endl, data($staffel/@href), $endl )'''.format(self.site),
					sjmanager.fsutil.Path(xmlfile.name))

		l = xquery_output
		assert len(l) % 2 == 0

		self.season_title_to_links = {}

		filtered_seasons = filter(
			self.__valid_season_title, 
			functools.reduce(
				lambda old,x: old + [(l[x],l[x+1])],
				range(0,len(l),2),
				[]))

		for season_title, season_link in filtered_seasons:
			mangled_season_title = self.__mangle_season_title(
				season_title)

			if mangled_season_title not in self.season_title_to_links:
				self.season_title_to_links[mangled_season_title] = [Show.SeasonCacheEntry(mangled_season_title,season_link,self.percent_callback_creator)]
			else:
				self.season_title_to_links[mangled_season_title].append(Show.SeasonCacheEntry(mangled_season_title,season_link,self.percent_callback_creator))

	class EpisodeReader:
		def __init__(self, source):
			self.lines = (line for line in source)
			self.line = None

		def __readline(self):
			try:
				self.line = next(self.lines)
			except StopIteration:
				self.line = None

		def __parse_block(self, block):
			ret = dict()
			self.__readline()
			while self.line and not self.line == ('END ' + block):
				sp = self.line.split(' ', 1)
				ret[sp[0]] = sp[1]
				self.__readline()
			return ret

		def __parse_season(self):
			header = []
			episodes = []
			if self.line == 'BEGIN HEADER':
				header = self.__parse_block('HEADER')
			while self.line and not self.line == 'BEGIN HEADER':
				if self.line == 'BEGIN EPISODE':
					episodes.append(
							self.__parse_block('EPISODE'))
				self.__readline()

			return (header, episodes)

		def read(self):
			"""
			Reads episodes from source and returns in the format
				[(header, [episode, …]), … ]
			where header and episode are dictionaries.
			"""
			seasons = []

			self.__readline()
			while self.line:
				seasons.append(
						self.__parse_season())

			return seasons

	class SeasonCacheEntry:
		def __init__(
			self,
			title,
			link,
			percent_callback_creator):

			assert isinstance(link,str)
			assert isinstance(title,str)

			self.title = title
			self.link = link
			self.seasons = None
			self.percent_callback_creator = percent_callback_creator

		def follow_link(
			self,
			html_converter,
			downloader,
			xquery_processor):
			with html_converter.convert(downloader.download(url = self.link,percent_callback = self.percent_callback_creator('Download episodes for season...'))) as xml_file:
				xquery_output = xquery_processor.run_file(
					sjmanager.fsutil.Path('xqueries')/'season_to_episodes.xquery',
					sjmanager.fsutil.Path(xml_file.name))

			self.seasons = []
			for season_dict,episodes in Show.EpisodeReader(xquery_output).read():
				self.seasons.append(
					Season(
						self.title,
						season_dict,
						episodes))



class Season:
	def __init__(
		self,
		title,
		information,
		episodes):
		"""
		Retrieves the information for the season (duration, size, ...) as well as
		the information about every episode. Internally, stores a list of episode
		objects.
		"""
		sjmanager.log.log('Season information: {}'.format(information))

		self.duration = information['duration']
		self.size = information['size']
		self.format = information['format']
		self.language = information['language']
		self.title = title

		self.episodes = []
		for episode in episodes:
			self.episodes.append(
				Episode(
					episode['title'],
					self.__mangle_episode_title(
						episode['title'],
						self.title),
					episode['link']))

	def episode_titles(self):
		"""
		Returns a set of mangled episode titles (strings).

		In the menu, to show all episodes in a specific season, you could take the
		union of all "episode_titles" in all seasons.
		"""
		result = set()
		for episode in self.episodes:
			result.add(
				episode.title)
		return result

	def episode(self,title):
		"""
		Returns the episode with the specified mangled title, or None, if it wasn't
		found in this season. This way, we can easily iterate over all season with
		a title and check if they contain the  specified episode
		"""
		assert isinstance(title,str)

		for episode in self.episodes:
			sjmanager.log.log('Episode title is {}'.format(episode.title))
			if episode.title == title:
				return episode

		return None

	def __mangle_episode_title(self, episode_title, season_title):
		assert isinstance(episode_title,str)
		assert isinstance(season_title,str)

		if season_title.isnumeric():
			# TODO: filter out wrong seasons?
			match = re.search(r'S0*' + season_title + 'E(?P<episode>\d+)', episode_title)
			if match:
				return str(int(match.group('episode')))
		match = re.search(r'E(?P<episode>\d+)', episode_title)
		if match:
			return str(int(match.group('episode')))
		# couldn't find a reasonable episode number, so return the title
		return episode_title


class Episode:
	def __init__(
		self,
		real_title,
		title,
		link):
		"""
		Constructs the object with title and link
		"""
		
		assert isinstance(real_title,str)
		assert isinstance(title,str)
		assert isinstance(link,str)

		self.real_title = real_title
		self.title = title
		self.link = link

