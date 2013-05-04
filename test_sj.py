#!/usr/bin/python3
import sjmanager.downloader.factory
import sjmanager.captcha.factory
import sjmanager.xquery_processor.factory
import sjmanager.html_to_xml.factory
import sjmanager.sql.factory
import sjmanager.config_directory
import sjmanager.sj
import sjmanager.menu
import sjmanager.ul
import sjmanager.util
import configparser
import sjmanager.downloader.meter

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

sql = sjmanager.sql.factory.create(
	config_file)

downloader = sjmanager.downloader.factory.create(
	config_file)

xquery_processor = sjmanager.xquery_processor.factory.create(
	config_file)

html_converter = sjmanager.html_to_xml.factory.create(
	config_file)

ul = sjmanager.ul.Account(
	('login',config_file.get('ul','cookie')),
	downloader)

captcha = sjmanager.captcha.factory.create(
	config_file)

print('Creating sj object')
sj = sjmanager.sj.Sj(
	config_file,
	sql,
	downloader,
	html_converter,
	xquery_processor,
	captcha,
	lambda x : sjmanager.downloader.meter.Simple(x))

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

exit(0)

print(sj.resolve_linklist(
	first_season[0].episode('1').link,
	sj.resolve_captcha_image))
