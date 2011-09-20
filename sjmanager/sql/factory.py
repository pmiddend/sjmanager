import sjmanager.sql.sqlite

def create(config_file):
	if sjmanager.sql.sqlite.Sqlite.available(config_file) == False:
		raise Exception('No sql backend was available (see the log for details)')
	
	return sjmanager.sql.sqlite.Sqlite(
		config_file)
