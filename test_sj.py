#!/usr/bin/python3
import sjmanager.sj
import sjmanager.config_directory
import sjmanager.sql.factory
import sjmanager.xquery_processor.factory
import sjmanager.downloader.factory
import sjmanager.html_to_xml.factory
import sjmanager.dialog
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

sql = sjmanager.sql.factory.create(
	config_file)

downloader = sjmanager.downloader.factory.create(
	config_file)

xquery = sjmanager.xquery_processor.factory.create(
	config_file)

html_converter = sjmanager.html_to_xml.factory.create(
	config_file,
	xquery)

print('Creating sj object')
sj = sjmanager.sj.Sj(
	config_file,
	sql,
	downloader,
	html_converter,
	xquery)

print('Testing find_show, searching for \"breaking\"')

shows_found = sj.find_shows(
	name = 'breaking')

if 'Breaking Bad' in [shows_found[0].name,shows_found[1].name] and 'Breaking In' in [shows_found[0].name,shows_found[1].name]:
	print('PASSED, got {}'.format([shows_found[0].name,shows_found[1].name]))
else:
	print('FAILED, got {}'.format([shows_found[0].name,shows_found[1].name]))
	exit(-1)

breaking_bad = shows_found[0] if shows_found[0].name == 'Breaking Bad' else shows_found[1]

print('Season titles are: {}'.format(breaking_bad.season_titles()))

print('Getting seasons for title "1"...')

first_season = breaking_bad.seasons('1')

for post in first_season:
	print('Episode titles for this post (duration {}) are: {}'.format(post.duration,post.episode_titles()))

print(sj.resolve_linklist(
	first_season[0].episode('1').link,
	sj.resolve_captcha_image))
