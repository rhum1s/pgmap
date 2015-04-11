# config.py
# R. Souweine, 2015

# TODO: Use unittest (http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-2/)

import psycopg2 as pg
import pandas.io.sql as psql
import geopandas as gpd
from config import Cfg


class Pg():
    def __init__(self, config_file):
        """
        :param config_file: The .ini type configuration text file.
        """
        cfg = Cfg(config_file)  # Reads config file
        self.conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % \
                           (cfg.pg_host, cfg.pg_port, cfg.pg_db, cfg.pg_lgn, cfg.pg_pwd)

    def execute(self, sql, notices=False):
        """
        Executes query in PostgreSQL.
        Can run multiple queries at a time.
        Transactions work as everything will be rolled back if error.
        :param sql: The query
        :param notices: Print PostgreSQL notices if there are.
        """
        con = pg.connect(self.conn_string)
        try:
            psql.execute(sql, con)
            con.commit()
            con.close()
        except psql.DatabaseError, e:
            print "ERROR", e
        con.close()

        # If notices print it
        if len(con.notices) > 0 and notices is True:
            for notice in con.notices:
                print notice.replace('\n', '')

    def select(self, sql):
        """
        Execute the query and return result in Pandas Dataframe.
        Connection is opened and closed each time.
        If SQL query contains errors, will return the SQL debug output.
        :param sql: The query
        :return: Pandas Dataframe
        """
        con = pg.connect(self.conn_string)
        dataframe = psql.read_sql(sql, con)
        con.close()
        return dataframe

    def geo_select(self, sql, geom_col='geom'):
        """
        Like select function put also extract geometry in WKT thanks to GeoPandas.
        """
        con = pg.connect(self.conn_string)
        geo_dataframe = gpd.read_postgis(sql, con, geom_col=geom_col)
        con.close()
        return geo_dataframe

if __name__ == "__main__":
    print "pg.py - Running tests ..."
    db = Pg("config.cfg")

    # Number of connections at start
    nb_conn1 = db.select("select sum(numbackends) as nb from pg_stat_database;").nb.values[0]

    # NOTE: The next test will create table, not that good in another person database.
    db.execute("drop table if exists toto; drop table if exists toto; create table public.toto(gid integer);", True)
    df = db.select("select gid, candidat, toponyme from bdcarthage.cours_d_eau limit 3;")
    gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 3;")

    # Verify if each connections where closed
    nb_conn2 = db.select("select sum(numbackends) as nb from pg_stat_database;").nb.values[0]
    if nb_conn2 <= nb_conn1:
        print "- Avoid multiple connections: Success (%s->%s)." % (nb_conn1, nb_conn2)
    else:
        print "ERROR: During test, not all connections where closed (%s->%s)." % (nb_conn1, nb_conn2)