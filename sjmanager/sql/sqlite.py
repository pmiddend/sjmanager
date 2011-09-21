import sqlite3
import sjmanager.cache_directory
import sjmanager.sql.base
import sjmanager.log

_database_schema = '''CREATE TABLE IF NOT EXISTS show
(
name TEXT NOT NULL,
url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS last_watched
(
show_url TEXT NOT NULL,
season_title TEXT NOT NULL,
episode_title TEXT NOT NULL,
finished int NOT NULL
);

CREATE TABLE IF NOT EXISTS downloaded
(
show_url TEXT NOT NULL,
season_title TEXT NOT NULL,
episode_title TEXT NOT NULL
);
'''

class Sqlite(sjmanager.sql.base.Base):
	def available(config_file):
		return True

	def __init__(self,config_file):
		db_file = config_file.get(
			'sqlite',
			'db_file',
			fallback = '$CACHE_DIR/db')

		db_file = db_file.replace(
			'$CACHE_DIR',
			str(sjmanager.cache_directory.cache_directory()))

		sjmanager.log.log('Database file is {}'.format(db_file))

		self.connection = sqlite3.connect(
			db_file)

		self.connection.row_factory = sqlite3.Row

		self.connection.executescript(
			_database_schema)

	def execute(
		self,
		statement,
		*args):
		assert isinstance(statement,str)
		return self.connection.execute(statement,*args)

	def executemany(
		self,
		statement,
		*args):
		assert isinstance(statement,str)
		return self.connection.executemany(statement,*args)

	def commit(
		self):
		self.connection.commit()
