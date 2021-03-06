# -*- coding:utf-8 -*-
# R. Souweine, 2015

import ConfigParser


class Cfg():
    def __init__(self, config_file):
        """
        Reads the config file and extracts params.
        :param config_file: Text file in .ini format.
        :return: An object containing all params.
        """
        self.config_file = config_file
        self.config_parser = ConfigParser.ConfigParser()
        self.config_parser.read(self.config_file)
        self.sections = self.config_parser.sections()

        # Retrieve PostgreSQL params
        self.pg_host = self.config_parser.get('PostgreSQL', 'host')
        self.pg_port = self.config_parser.get('PostgreSQL', 'port')
        self.pg_db = self.config_parser.get('PostgreSQL', 'db')
        self.pg_lgn = self.config_parser.get('PostgreSQL', 'login')
        self.pg_pwd = self.config_parser.get('PostgreSQL', 'password')

if __name__ == "__main__":

    import os
    import unittest

    class TestFunctionsPg(unittest.TestCase):

        print "Testing", os.path.basename(__file__)

        def test_file_reading(self):
            Cfg("config.cfg.example")

    unittest.main()