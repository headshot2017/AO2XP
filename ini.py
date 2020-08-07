from ConfigParser import ConfigParser
from PyQt4.QtCore import QString
from os.path import exists

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

def read_sectionless_ini(file, search, default=""):
    if isinstance(file, QString): file = str(file)
    if isinstance(search, QString): search = str(search)

    with open(file) as f:
        for keys in f.read().split("\n"):
            if not keys or "=" not in keys: continue

            key, value = keys.split("=")
            if search.lower() == key.rstrip().lower():
                return value.lstrip()
    return default

# AO 2.8

def get_img_suffix(path):
    if exists(path): return path
    if exists(path+".webp"): return path+".webp"
    if exists(path+".apng"): return path+".apng"
    if exists(path+".gif"): return path+".gif"
    return path+".png"

def read_ini_tags(file, target_tag):
    if isinstance(file, str) or isinstance(file, QString):
        conf = ConfigParser()
        conf.read(str(file))
    else:
        conf = file

    r_values = []

    if target_tag:
        try: keys = conf.options(target_tag)
        except: return []

        for key in keys:
            value = conf.get(target_tag, key)
            r_values.append(key+"="+value)

    else:
        for sect in conf.sections():
            keys = conf.options(sect)
            for key in keys:
                value = conf.get(target_tag, key)
                r_values.append(key+"="+value)

    return r_values

def get_effect_sound(fx_name, char):
    p_effect = read_ini("base/characters/"+char+"/char.ini", "options", "effects")
    p_path = "base/misc/"+p_effect+"/effects.ini"
    default_path = "AO2XPbase/themes/default/effects/effects.ini"
    
    if exists(p_path):
        return read_sectionless_ini(p_path, fx_name)
    return read_sectionless_ini(default_path, fx_name)

def get_effects(char):
    p_effect = read_ini("base/characters/"+char+"/char.ini", "options", "effects")
    p_path = "base/misc/"+p_effect+"/effects.ini"

    effects = ["realization", "hearts", "reaction", "impact"]
    if not exists(p_path): return effects

    lines = open(p_path).read().split("\n")
    for line in lines:
        effect = line.split("=")[0].rstrip()
        if effect and effect not in effects:
            effects.append(effect)

    return effects

def get_effect(effect, char, folder):
    p_effect = folder
    if not p_effect: p_effect = read_ini("base/characters/"+char+"/char.ini", "options", "effects")
    p_path = get_img_suffix("base/misc/"+p_effect+"/"+effect)
    default_path = get_img_suffix("AO2XPbase/themes/default/effects/"+effect)

    if not exists(p_path):
        return default_path
    return p_path