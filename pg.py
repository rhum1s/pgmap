# config.py
# R. Souweine, 2015

# TODO: Use unittest (https://github.com/geopandas/geopandas/commit/5bae14a9f4aa56978e06485f6b19399a9b335686)

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

    def execute(self, sql):
        """
        Executes query in PostgreSQL.
        """
        # TODO: Seems to be able to exec multiple queries on one time.
        # TODO: Be able to display outputs of execute queries.
        con = pg.connect(self.conn_string)
        psql.execute(sql, con)
        con.close()

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
        # TODO: Extract XY?
        con = pg.connect(self.conn_string)
        geo_dataframe = gpd.read_postgis(sql, con, geom_col=geom_col)
        con.close()
        return geo_dataframe

if __name__ == "__main__":
    print "pg.py - Running tests ..."
    db = Pg("config.cfg")

    # Avoid multiple connections test
    nb_conn1 = db.select("select sum(numbackends) as nb from pg_stat_database;").nb.values[0]
    db.execute("drop table if exists toto; create temporary table toto (gid integer);")
    df = db.select("select gid, candidat, toponyme from bdcarthage.cours_d_eau limit 3;")
    gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 3;")
    nb_conn2 = db.select("select sum(numbackends) as nb from pg_stat_database;").nb.values[0]
    if nb_conn2 <= nb_conn1:
        print "- Avoid multiple connections: Success (%s->%s)." % (nb_conn1, nb_conn2)