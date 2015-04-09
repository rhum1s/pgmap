#/usr/bin/python
# config.py
# R. Souweine, 2015

import ConfigParser

def read_config(config_file):
    the_config = ConfigParser.ConfigParser()
    the_config.read(config_file)
    return the_config

def map_config_section(config_object, section):
    """
    Reads a defined section of a config object.
    NOTE: To read a boolean: Config.getboolean(section, option)
    """
    config_dict = {}
    options = config_object.options(section)
    for option in options:
        try:
            config_dict[option] = config_object.get(section, option)
            if config_dict[option] == -1:
                print("DEBUG: Skip: %s" % option)
        except:
            print("ERROR: Exception on %s!" % option)
            config_dict[option] = None
    return config_dict

if __name__ == "__main__":
    
    # Read config file
    config = read_config("config.cfg")
    cfg_pg = map_config_section(config, "PostgreSQL")

    print cfg_pg
