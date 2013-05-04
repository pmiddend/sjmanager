import sjmanager.rs
import sjmanager.config_directory
import sjmanager.downloader.factory
import sjmanager.downloader.meter
import configparser

config_file = configparser.ConfigParser()
config_file.read(
	str(
		sjmanager.config_directory.config_directory() / "config.ini"))

downloader = sjmanager.downloader.factory.create(
	config_file)

locations = downloader.track_link('http://download.serienjunkies.org/go-d867158819aad480638e5c96e3986a5e78dd62d2272b20849b10b7767a114e897c79928c850ea28211be349eb8adfbc3/')

for location in locations:
    print(location)
