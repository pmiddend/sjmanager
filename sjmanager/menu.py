import sjmanager.sj
import sjmanager.states
import sjmanager.dialog
import sjmanager.rar

import tempfile
import shutil
import os
import shlex
import subprocess
import mimetypes
import urllib.parse
import os.path
import re

class Menu:
	def __init__(
		self,
		ul,
		sj,
		downloader,
		xquery_processor,
		sql):

		assert isinstance(ul,sjmanager.ul.Account)
		assert isinstance(sj,sjmanager.sj.Sj)
		assert isinstance(downloader,sjmanager.downloader.base.Base)
		assert isinstance(xquery_processor,sjmanager.xquery_processor.base.Base)
		assert isinstance(sql,sjmanager.sql.base.Base)

		self.ul = ul
		self.sj = sj
		self.downloader = downloader
		self.xquery_processor = xquery_processor
		self.sql = sql

		self.state_set = {
			'continue_or_new_show' : {'requires' : set(),'provides' : {'continue_or_new'}},
			'ask_for_show_search_string' : {'requires' : set(),'provides' : {'search_string'}},
			'no_shows_found' : {'requires' : set(),'provides' : set(),'nohistory' : True},
			'choose_new_show_from_list' : {'requires' : {'search_string'},'provides' : {'current_show'}},
			'choose_season' : {'requires' : {'current_show'},'provides' : {'season_title'}},
			'choose_episode' : {'requires' : {'season_title'},'provides' : {'episode_title'}},
			'choose_quality' : {'requires' : {'season_title','episode_title'},'provides' : {'episode_link'}},
			'resolve_linklist' : {'requires' : {'episode_link'},'provides' : {'linklist'}},
			'wrong_captcha' : {'requires' : set(),'provides' : set(),'nohistory' : True},
			'download_error' : {'requires' : {'download_error'},'provides' : set(),'nohistory' : True},
			'download_or_play' : {'requires' : {'current_show','season_title','episode_title'},'provides' : set(),'nohistory' : True},
			'download' : {'requires' : {'linklist'},'provides' : {'download_error'}},
			'choose_continue_show' : {'requires' : set(),'provides' : {'current_show'}},
			'no_shows_in_cache' : {'requires' : set(),'provides' : set(),'nohistory' : True},
			'play' : {'requires' : {'season_title','episode_title','current_show'},'provides' : set()},
			'finished_watching' : {'requires' : {'season_title','episode_title','current_show'},'provides' : {'finished_watching'}},
			'delete_from_cache' : {'requires' : {'season_title','episode_title','current_show','finished_watching'},'provides' : set()},
			'determine_next_episode' : {'requires' : {'current_show'},'provides' : {'season_title','episode_title'},'nohistory' : True},
		}

		self.menu_transitions = [
			{
				'from' : 'continue_or_new_show', 'to' : 'ask_for_show_search_string',
				'condition' : lambda result,menu : result['continue_or_new'] == 'new'
			},

			# There are shows in the cache, so we can continue
			{
				'from' : 'continue_or_new_show', 'to' : 'choose_continue_show',
				'condition' : lambda result,menu : result['continue_or_new'] == 'continue' and menu.sj.shows_in_watch_cache()
			},

			{
				'from' : 'choose_continue_show', 'to' : 'determine_next_episode'
			},

			{
				'from' : 'determine_next_episode', 'to' : 'choose_season',
				'condition' : lambda result,menu : result['season_title'] == None
			},

			{
				'from' : 'determine_next_episode', 'to' : 'choose_episode',
				'condition' : lambda result,menu : result['episode_title'] == None
			},

			{
				'from' : 'determine_next_episode', 'to' : 'download_or_play',
				'condition' : lambda result,menu : result['episode_title'] != None and result['season_title'] != None
			},

			# There are no shows in the cache, show an error and return
			{
				'from' : 'continue_or_new_show', 'to' : 'no_shows_in_cache',
				'condition' : lambda result,menu : result['continue_or_new'] == 'continue' and not menu.sj.shows_in_watch_cache()
			},

			{
				'from' : 'no_shows_in_cache', 'to' : 'continue_or_new_show'
			},

			# Search string empty
			{
				'from' : 'ask_for_show_search_string', 'to' : 'ask_for_show_search_string',
				'condition' : lambda result,menu : len(result['search_string']) == 0
			},

			# Search string correct, choose show (if there are any)
			{
				'from' : 'ask_for_show_search_string', 'to' : 'choose_new_show_from_list',
				'condition' : lambda result,menu : len(result['search_string']) != 0
			},

			{
				'from' : 'choose_new_show_from_list', 'to' : 'no_shows_found',
				'condition' : lambda result,menu : result['current_show'] == None
			},

			{
				'from' : 'no_shows_found', 'to' : 'ask_for_show_search_string'
			},

			{
				'from' : 'choose_new_show_from_list', 'to' : 'choose_season'
			},

			{
				'from' : 'choose_season', 'to' : 'choose_episode'
			},

			{
				'from' :  'choose_episode', 'to' : 'download_or_play'
			},

			{
				'from' :  'download_or_play', 'to' :  'choose_quality',
				'condition' : lambda result,menu : not result['current_show'].episode_in_cache(result['season_title'],result['episode_title'])
			},

			{
				'from' :  'download_or_play', 'to' :  'play',
				'condition' : lambda result,menu : result['current_show'].episode_in_cache(result['season_title'],result['episode_title'])
			},

			{
				'from' : 'choose_quality', 'to' : 'resolve_linklist'
			},

			{
				'from' : 'resolve_linklist', 'to' : 'wrong_captcha',
				'condition' : lambda result,menu : result['linklist'] != None and len(result['linklist']) == 0
			},

			{
				'from' : 'wrong_captcha', 'to' : 'resolve_linklist'
			},

			{
				'from' : 'resolve_linklist', 'to' : 'download',
				'condition' : lambda result,menu : result['linklist'] != None and len(result['linklist']) != 0
			},

			{
				'from' : 'download', 'to' : 'download_error',
				'condition' : lambda result,menu : len(result['download_error']) != 0
			},

			{
				'from' : 'download_error', 'to' : 'choose_quality'
			},

			{
				'from' : 'download', 'to' : 'play',
				'condition' : lambda result,menu : len(result['download_error']) == False
			},

			{
				'from' : 'play', 'to' : 'finished_watching'
			},

			{
				'from' : 'finished_watching', 'to' : 'delete_from_cache',
				'condition' : lambda result,menu : result['finished_watching'] == True
			},

			{
				'from' : 'finished_watching', 'to' : 'continue_or_new_show',
				'condition' : lambda result,menu : result['finished_watching'] == False
			},

			{
				'from' : 'delete_from_cache', 'to' : 'continue_or_new_show'
			},
		]
	
	def run(
		self):

		sjmanager.states.execute_state_machine(
			self,
			self.state_set,
			'continue_or_new_show',
			self.menu_transitions)

	def continue_or_new_show(
		self,
		result):

		menu_return, selection = sjmanager.dialog.show_menu(
			'Choose what do do next...',
			[ 
				(1,'Continue a show'), 
				(2,'Watch something new') 
			])

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_exit()

		if selection[0] == 1:
			result['continue_or_new'] = 'continue'
		else:
			result['continue_or_new'] = 'new'

		return sjmanager.states.return_code_forward()

	def no_shows_in_cache(
		self,
		result):

		sjmanager.dialog.show_messagebox(
			"You didn't start to watch any shows yet...")

		return sjmanager.states.return_code_forward()

	def choose_continue_show(
		self,
		result):
		"""
		Ask the user which show to continue
		"""

		menu_items = []
		urls = []

		# Select the show URLs from the last_watched table and join the show table
		# to get the title
		for row in self.sql.execute('SELECT show.name show_name,show_url FROM last_watched LEFT JOIN show ON (show.url = show_url) ORDER BY show.name'):
			menu_items.append(
				(len(menu_items),row['show_name']))
			urls.append(
				row['show_url'])

		menu_return, selection = sjmanager.dialog.show_menu(
			'Which show to continue...',
			menu_items)

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_back()

		selected_url = urls[selection[0]]

		# Find shows can search by URL, but for consistency, it still returns an
		# array of shows.
		found_shows = self.sj.find_shows(
			url = selected_url)

		result['current_show'] = found_shows[0]

		return sjmanager.states.return_code_forward()

	def ask_for_show_search_string(
		self,
		result):

		"""
		The user chose to watch something new, so ask him for a show search string
		"""

		# We might have a search string from a previous search in result
		menu_return, text_entered = sjmanager.dialog.show_inputbox(
			'Enter show search string:',
			result['search_string'] if 'search_string' in result else '')

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_back()

		result['search_string'] = text_entered
		return sjmanager.states.return_code_forward()

	def no_shows_found(
		self,
		result):

		"""
		Transient state, showing that the search for a show didn't succeed

		Requires: search_string
		"""
		assert isinstance(result['search_string'],str)

		sjmanager.dialog.show_messagebox(
			'No shows matching "{}" found!'.format(
				result['search_string']))

		return sjmanager.states.return_code_forward()

	def choose_new_show_from_list(
		self,
		result):

		"""
		We've found some shows matching the search string. Now let the user choose
		one.

		Requires: search_string
		Provides: current_show
		"""
		assert isinstance(result['search_string'],str)

		candidates = self.sj.find_shows(
			name = result['search_string'])

		# No candidates found, return some kind of error code: set the current show
		# to None
		if len(candidates) == 0:
			result['current_show'] = None
			return sjmanager.states.return_code_forward()

		show_menu = []
		for current_show in candidates:
			show_menu.append((
				len(
					show_menu),
				current_show.name))

		menu_return, selection = sjmanager.dialog.show_menu(
			'Which show...',
			show_menu)

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_back()

		result['current_show'] = candidates[selection[0]]

		return sjmanager.states.return_code_forward()

	def choose_season(
		self,
		result):

		"""
		We've got a show in current_show (either by continuing or by selecting
		"watch something new"), but no seasons, or no seasons anymore.

		Requires: current_show
		Provides: season_title
		"""
		assert isinstance(result['current_show'],sjmanager.sj.Show)

		sorted_season_titles = list(result['current_show'].season_titles())
		sorted_season_titles.sort(
			key = lambda x : int(x) if x.isnumeric() else 2**32)

		menu_return, selection = sjmanager.dialog.show_menu(
				'Which season...',
				[
					(i, '')
					for i in sorted_season_titles
				],
				title = result['current_show'].name)

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_back()

		result['season_title'] = selection[0]

		return sjmanager.states.return_code_forward()

	def choose_episode(
		self,
		result):

		"""
		Requires: seasons
		Provides: episode_title
		"""
		assert isinstance(result['current_show'],sjmanager.sj.Show)
		assert isinstance(result['season_title'],str)

		episode_titles = set()
		for season in result['current_show'].seasons(result['season_title']):
			episode_titles = episode_titles.union(
				season.episode_titles())

		sorted_episode_titles = list(episode_titles)
		sorted_episode_titles.sort(
			key = lambda x : int(x) if x.isnumeric() else 2**32)

		menu_return, selection = sjmanager.dialog.show_menu(
				'Which episode...',
				[ (i,'') for i in sorted_episode_titles],
				title = '{}, Season {}'.format(
					result['current_show'].name,
					result['season_title']))

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_back()

		result['episode_title'] = selection[0]

		return sjmanager.states.return_code_forward()

	def determine_next_episode(
		self,
		result):

		"""
		Given a show, determine the mangled season title and mangled episode title
		of the next episode.

		Requires: current_show
		Provides: season_title, episode_title
		"""

		assert isinstance(result['current_show'],sjmanager.sj.Show)

		# determine_next_episode will return a dictionary containing the episode
		# title and the season title. Or None, if none could be found
		next_episode_information = result['current_show'].determine_next_episode()

		assert 'season_title' in next_episode_information and 'episode_title' in next_episode_information

		result['season_title'] = next_episode_information['season_title']
		result['episode_title'] = next_episode_information['episode_title']

		return sjmanager.states.return_code_forward()

	def choose_quality(self,result):
		"""
		Given a show, a season title and an episode title, determine the quality
		level

		Requires: current_show, season_title, episode_title
		"""
		def shorten_title(title):
			if len(title) < 60:
				return title
			return title[0:59]+'…'

		def shorten_language(lang):
			uppered = lang.upper()
			result = ''
			if 'DEUTSCH' in uppered or 'GERMAN' in uppered:
				result += 'GER '
			else:
				result += '    '
			if 'ENGLISCH' in uppered or 'ENGLISH' in uppered:
				result += 'ENG'
			else:
				result += '   '
			return result

		assert isinstance(result['current_show'],sjmanager.sj.Show)
		assert isinstance(result['season_title'],str)
		assert isinstance(result['episode_title'],str)

		# First, get all seasons, then for each season, get all episodes with the
		# title we want, as well as the quality information
		seasons = result['current_show'].seasons(
			result['season_title'])

		sjmanager.log.log('There are {} seasons with that episode'.format(len(seasons)))

		menu_items = []

		index = -1
		for season in seasons:
			index += 1

			this_episode = season.episode(
				result['episode_title'])
			# It could be that not all seasons contain all episodes
			if this_episode == None:
				continue
			menu_items.append((
				index,
				shorten_language(
					season.language)+
				'\t\t'+
				season.size+
				'\t\t'+
				shorten_title(
					this_episode.real_title)))

		menu_return, selection = sjmanager.dialog.show_menu(
			'Which quality...',
			menu_items,
			title = '{}, Season {}, Episode {}'.format(
				result['current_show'].name,
				result['season_title'],
				result['episode_title']))

		if menu_return != sjmanager.dialog.MenuReturn.ok:
			return sjmanager.states.return_code_back()

		result['episode_link'] = seasons[selection[0]].episode(
			result['episode_title']).link

		return sjmanager.states.return_code_forward()

	def resolve_linklist(self,result):
		"""
		Given an episode link, resolve the link to a linklist

		Requires: episode_link
		Provides: linklist
		"""
		assert isinstance(result['episode_link'],str)

		result['linklist'] = self.sj.resolve_linklist(
			result['episode_link'])

		if result['linklist'] == None:
			return sjmanager.states.return_code_back(1)

		# This will take us back to "ourselves"
		if result['linklist'] == None or len(result['linklist']) == 0:
			return sjmanager.states.return_code_forward()

		linklist = []
		for raw_link in result['linklist']:
			linklist.append(
				self.ul.make_proper_link(
					raw_link))

		result['linklist'] = linklist

		return sjmanager.states.return_code_forward()

	def wrong_captcha(self,result):
		sjmanager.dialog.show_messagebox('Wrong CAPTCHA, try again')
		return sjmanager.states.return_code_forward()

	def download_error(self,result):
		sjmanager.dialog.show_messagebox('An error occured while downloading: '+result['download_error'])
		# 1 -> download
		# 2 -> resolve_linklist
		# 3 -> choose_quality
		return sjmanager.states.return_code_back(3)

	def play(self,result):
		"""
		Expects a show, a season and an episode title and tries to play the show from the cache.
		"""

		assert isinstance(result['current_show'],sjmanager.sj.Show)
		assert isinstance(result['season_title'],str)
		assert isinstance(result['episode_title'],str)

		file_name = sjmanager.cache_directory.cache_directory() / 'download_cache' / self.sj.video_file_name(
			result['current_show'].url,
			result['season_title'],
			result['episode_title'])

		sjmanager.log.log('Looking for episode in cache (it has to be there!): {}'.format(file_name))

		assert file_name.is_file()

		movie_player = self.sj.config_file.get('global','movie_player').strip()

		sjmanager.log.log('Movie player found: {}'.format(movie_player))

		movie_player_command_args = shlex.split(
				movie_player)

		if self.sql.execute('SELECT COUNT(*) c FROM last_watched WHERE show_url = ?',(result['current_show'].url,)).fetchone()['c'] > 0:
			sjmanager.log.log("There already is a cache entry for this show, updating that")
			self.sql.execute_and_commit('UPDATE last_watched SET season_title = ?, episode_title = ?, finished = 0 WHERE show_url = ?',(result['season_title'],result['episode_title'],result['current_show'].url))
		else:
			sjmanager.log.log("There no watch cache entry yet, inserting")
			self.sql.execute_and_commit('INSERT INTO last_watched (show_url,season_title,episode_title,finished) VALUES (?,?,?,?)',(result['current_show'].url,result['season_title'],result['episode_title'],0))

		sjmanager.log.log('Calling: {}'.format(movie_player_command_args + [file_name]))
		subprocess.call(
			movie_player_command_args + [str(file_name)])

		return sjmanager.states.return_code_forward()

	def finished_watching(
		self,
		result):

		assert isinstance(result['current_show'],sjmanager.sj.Show)

		result['finished_watching'] = sjmanager.dialog.show_yesno('Have you finished watching the episode?')

		if result['finished_watching'] == True:
			self.sql.execute_and_commit('UPDATE last_watched SET finished = 1 WHERE show_url = ?',(result['current_show'].url,))

		return sjmanager.states.return_code_forward()

	def delete_from_cache(
		self,
		result):

		assert isinstance(result['current_show'],sjmanager.sj.Show)
		assert isinstance(result['season_title'],str)
		assert isinstance(result['episode_title'],str)

		really_delete_from_cache = sjmanager.dialog.show_yesno('Do you want to delete the episode from the cache?')

		if really_delete_from_cache:
			(sjmanager.cache_directory.cache_directory() / 'download_cache' / self.sj.video_file_name(
				result['current_show'].url,
				result['season_title'],
				result['episode_title'])).remove()

			self.sql.execute_and_commit('DELETE FROM downloaded WHERE show_url = ? AND season_title = ? AND episode_title = ?',(result['current_show'].url,result['season_title'],result['episode_title']))

		return sjmanager.states.return_code_forward()

	def download(self,result):
		result['download_error'] = ''

		try:
			link_pm = sjmanager.dialog.ProgressMeter(
				'Checking links...')

			link_pm.update(
				0)

			counter = 1
			# Ok, we've got the links. Check if they're valid (one by one)
			for link in result['linklist']:
				result_code,result_string = self.ul.check_link(
					link)

				link_pm.update(
					int(
						counter/len(result['linklist']) * 100))

				counter += 1

				# If one of them is not valid, display a message and return
				if not result_code == sjmanager.ul.CheckLink.ok:
					link_pm.close()
					result['download_error'] = 'At least one link was not valid. The reason is:\n\n'+result_string+'\n\nTaking you back to the quality chooser'
					return sjmanager.states.return_code_forward()
		finally:
			link_pm.close()

		# Ok, now we know all links are valid, we can begin downloading them
		counter = 1
		with tempfile.TemporaryDirectory() as tempdir_raw:
			tempdir = sjmanager.util.Path(
				tempdir_raw)

			sjmanager.log.log('Created a temporary directory '+str(tempdir))

			for link in result['linklist']:
				self.ul.download(
					url = link,
					output_file_path = tempdir / os.path.basename(urllib.parse.urlparse(link).path),
					percent_callback = sjmanager.downloader.meter.Dialog(
						'Downloading part {0} of {1}'.format(
							counter,
							len(
								result['linklist']))))
				counter += 1

			# Ok, we've got all the links, now extract the first one
			first_file_name = tempdir / os.path.basename(urllib.parse.urlparse(result['linklist'][0]).path)

			sjmanager.log.log('Unrarring '+str(first_file_name))

			passwords_raw = self.sj.config_file.get('global', 'passwords')
			passwords = passwords_raw.split(',')
			passwords = list(map(str.strip,passwords))

			accumulated_errorstring = ''
			password_worked = False
			for password in passwords:
				sjmanager.log.log('Trying password '+password)

				error_string = sjmanager.rar.unrar(
					filename = first_file_name,
					working_dir = tempdir,
					password = password,
					title = 'Extracting...')

				if error_string == None:
					password_worked = True
					break
				else:
					sjmanager.log.log('unrar error: '+str(error_string,encoding='utf8'))
					accumulated_errorstring += 'unrar failed with the following error message: {}'.format(str(error_string,encoding='utf8'))

			if password_worked == False:
				result['download_error'] = accumulated_errorstring
				return sjmanager.states.return_code_forward()

			for root, dirnames, filenames in os.walk(str(tempdir)):
				for current_file_raw in filenames:
					current_file = os.path.join(
						root,
						current_file_raw)

					if not re.search(r'\.(avi|mpe?g|wmv|mkv|mp4)$',current_file):
						# returns (type_string,encoding)
						mime_guess = mimetypes.guess_type(
							current_file)

						sjmanager.log.log('Mime guess for {}: {}'.format(current_file,mime_guess))

						if not mime_guess[0] or not re.search(r'^video/.*$',mime_guess[0]):
							continue

					sjmanager.log.log('Video file file name is '+current_file)

					download_cache_dir = sjmanager.cache_directory.cache_directory() / 'download_cache'

					sjmanager.log.log('(optionally) creating download cache dir {}'.format(str(download_cache_dir)))

					if not download_cache_dir.is_directory():
						download_cache_dir.mkdir_recursive()

					hashed_filename = self.sj.video_file_name(
						result['current_show'].url,
						result['season_title'],
						result['episode_title'])

					sjmanager.log.log('Hashed filename is {}'.format(hashed_filename))
					sjmanager.log.log('Moving file {} to {}'.format(
						os.path.abspath(
							current_file),
						str(
							download_cache_dir / hashed_filename)))

					shutil.move(
						current_file,
						str(
							download_cache_dir / hashed_filename))

					sjmanager.log.log('Making a database entry for the downloaded show')
					self.sql.execute_and_commit('INSERT INTO downloaded (show_url,season_title,episode_title) VALUES (?,?,?)',(result['current_show'].url,result['season_title'],result['episode_title']))
					sjmanager.dialog.show_messagebox("Just press OK.")
					sjmanager.log.log('Continuing')

					return sjmanager.states.return_code_forward()

		result['download_error'] = "Didn't find any video files in the archive"
		return sjmanager.states.return_code_forward()

	def download_or_play(self,result):
		return sjmanager.states.return_code_forward()
