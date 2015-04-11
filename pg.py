# config.py
# R. Souweine, 2015

import psycopg2 as pg
import pandas.io.sql as psql
from config import Cfg


class Pg():
    def __init__(self, config_file):
        """
        :param config_file:
        :return:
        """
        cfg = Cfg(config_file)  # Reads config file

        self.conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % \
                           (cfg.pg_host, cfg.pg_port, cfg.pg_db, cfg.pg_lgn, cfg.pg_pwd)

    def select(self, sql):
        """
        Execute the query and return result in Pandas Dataframe.
        Connection is opened and closed each time.
        If SQL query contains errors, will return the SQL debug output.
        :param sql: The query
        :return: Pandas Dataframe
        """
        # TODO: Test if creates multiple connections
        con = pg.connect(self.conn_string)
        dataframe = psql.frame_query(sql, con)
        con.close()
        return dataframe

if __name__ == "__main__":
    print "pg.py - Running tests ..."
    db = Pg("config.cfg")
    df = db.select("select gid, candidat, toponyme from bdcarthage.cours_d_eau limit 0;")
    print df.to_string()


