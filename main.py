#!/usr/bin/env python3

import sjmanager.downloader.factory
import sjmanager.captcha.factory
import sjmanager.xquery_processor.factory
import sjmanager.html_to_xml.factory
import sjmanager.sql.factory
import sjmanager.config_directory
import sjmanager.sj
import sjmanager.menu
import sjmanager.rs
import sjmanager.util
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

downloader = sjmanager.downloader.factory.create(
	config_file)

xquery_processor = sjmanager.xquery_processor.factory.create(
	config_file)

html_converter = sjmanager.html_to_xml.factory.create(
	config_file)

sql = sjmanager.sql.factory.create(
	config_file)

rs = sjmanager.rs.Account(
	('enc',config_file.get('rs','cookie')),
	downloader)

captcha = sjmanager.captcha.factory.create(
	config_file)

sj = sjmanager.sj.Sj(
	config_file,
	sql,
	downloader,
	html_converter,
	xquery_processor,
	captcha)

m = sjmanager.menu.Menu(
	rs,
	sj,
	downloader,
	xquery_processor,
	sql)

m.run()
