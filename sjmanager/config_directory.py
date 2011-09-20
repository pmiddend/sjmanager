import os
import sjmanager.util

_config_directory = None

if 'XDG_CONFIG_HOME' in os.environ:
	_config_directory = sjmanager.util.Path(
		os.environ['XDG_CONFIG_HOME'])
else:
	assert 'HOME' in os.environ, 'Not even $HOME is defined, what the fuck is wrong here?!'
	_config_directory = sjmanager.util.Path(os.environ['HOME']) / ".config"

assert _config_directory != None

_config_directory = _config_directory / "sjmanager"

if _config_directory.is_directory() == False:
	_config_directory.mkdir_recursive()

def config_directory():
	return _config_directory
