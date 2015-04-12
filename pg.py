# config.py
# R. Souweine, 2015
# FIXME: Tests relies on my own db. Maybe must create a test db?

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
        psql.execute(sql, con)
        con.commit()
        con.close()
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
        :return: Pandas DataFrame
        """
        con = pg.connect(self.conn_string)
        dataframe = psql.read_sql(sql, con)
        con.close()
        return dataframe

    def geo_select(self, sql, geom_col='geom'):
        """
        Like select function put also extract geometry in WKT thanks to GeoPandas.
        NOTE: Output geometry column is always renamed geom.
        :return: Pandas DataFrame
        """
        con = pg.connect(self.conn_string)
        geo_dataframe = gpd.read_postgis(sql, con, geom_col=geom_col)

        if geom_col != "geom":
            geo_dataframe.rename(columns={geom_col: "geom"}, inplace=True)

        con.close()
        return geo_dataframe

    @staticmethod
    def nb_conn():
        """
        :return: Number of connections to the database.
        """
        return db.select("select sum(numbackends) as nb from pg_stat_database;").nb.values[0]

if __name__ == "__main__":

    import os
    import pandas as pd
    import pandas.core.series
    import unittest

    db = Pg("config.cfg")

    class TestFunctionsPg(unittest.TestCase):

        print "Testing", os.path.basename(__file__)

        def test_select(self):
            df = db.select("select gid, candidat, toponyme from bdcarthage.cours_d_eau limit 3;")
            self.assertIsInstance(df, pd.DataFrame)

        def test_geo_select(self):
            gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 3;")
            self.assertIsInstance(gdf, pd.DataFrame)

        def test_geo_select_geo_column(self):
            gdf = db.geo_select("select * from inventaires_emissions.inventaire_objets limit 10", "the_geom")
            self.assertIsInstance(gdf["geom"], pd.core.series.Series)

        def test_execute(self):
            self.assertRaises(psql.DatabaseError, db.execute("""
                drop table if exists public.pgmap_tests; create table public.pgmap_tests(gid integer);"""))

        def test_nb_con(self):
            nb_conn = db.nb_conn()
            self.assertIsInstance(nb_conn, int)

        def test_connections_closed(self):
            nb_conn_start = db.nb_conn()
            db.select("select gid, candidat, toponyme from bdcarthage.cours_d_eau limit 3;")
            db.geo_select("select * from bdcarthage.cours_d_eau limit 3;")
            nb_conn_end = db.nb_conn()
            nb_conn_diff = nb_conn_start - nb_conn_end
            self.assertEqual(nb_conn_diff, 0)

    unittest.main()
