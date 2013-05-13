import os
import sjmanager.fsutil

_cache_directory = None

if 'XDG_CACHE_HOME' in os.environ:
	_cache_directory = sjmanager.fsutil.Path(
		os.environ['XDG_CACHE_HOME'])
else:
	assert 'HOME' in os.environ, 'Not even $HOME is defined, what the fuck is wrong here?!'
	_cache_directory = sjmanager.fsfsutil.Path(os.environ['HOME']) / ".cache"

assert _cache_directory != None

_cache_directory = _cache_directory / "sjmanager"

if not _cache_directory.is_directory():
	_cache_directory.mkdir_recursive()

def cache_directory():
	return _cache_directory
