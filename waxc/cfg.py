import configparser

def read(fp):
	ini = configparser.ConfigParser()
	ini.read(fp, 'utf-8')
	
	return ini['DEFAULT']
