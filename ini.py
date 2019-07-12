from ConfigParser import ConfigParser
from PyQt4.QtCore import QString

def read_ini(file, section, value, default=""):
	if isinstance(file, str) or isinstance(file, QString):
		conf = ConfigParser()
		conf.read(str(file))
	else:
		conf = file
		
	values = conf.sections()
	for val in values:
		if val.lower() == section.lower():
			for c in conf.options(val):
				if c.lower() == value.lower():
					return conf.get(val, c)
	return default

def read_ini_bool(file, section, value, default=False):
	if isinstance(file, str) or isinstance(file, QString):
		conf = ConfigParser()
		conf.read(str(file))
	else:
		conf = file
	
	values = conf.sections()
	for val in values:
		if val.lower() == section.lower():
			for c in conf.options(val):
				if c.lower() == value.lower():
					return conf.getboolean(val, c)
	return default

def read_ini_int(file, section, value, default=0):
	if isinstance(file, str) or isinstance(file, QString):
		conf = ConfigParser()
		conf.read(str(file))
	else:
		conf = file
	
	values = conf.sections()
	for val in values:
		if val.lower() == section.lower():
			for c in conf.options(val):
				if c.lower() == value.lower():
					return conf.getint(val, c)
	return default