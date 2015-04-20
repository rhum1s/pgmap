# -*- coding:utf-8 -*-
# R. Souweine, 2015

import matplotlib
matplotlib.use("WXagg")
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from numpy import asarray
from geo_df_utils import calculate_bbox, extract_points_xy, projection, global_geometry_type


class PgMap():
    def __init__(self, config_file):
        """
        Object allowing to plot a query result

        Colormaps for GeoPandas plots - PgMap.show():
        binary
        Blues
        YlOrRd
        ...

        :param config_file:
        :return:
        """
        self.config_file = config_file
        self.db = Pg(self.config_file)
        self.map_width = 12.0
        self.map_height = 12.0

        # Map background options:
        self.map_countries = True
        self.map_countries_boundary_color = "grey"
        self.map_countries_boundary_width = 0.5
        self.map_coastlines = True
        self.map_coastlines_width = 0.5
        self.map_coastlines_color = "grey"
        self.map_fill_continents = True
        self.map_continents_color = "lightgrey"
        self.map_continents_color_lake = "white"
        self.map_continents_alpha = 0.2
        self.map_shaded_relief = True

        # Map files options
        self.dpi = 100

    def reload_config(self, config_file):
        self.config_file = config_file
        self.db = Pg(self.config_file)

    def map_general(self, bbox, resolution, proj):
        """
        Apply rcParams and creates the map object with a bounding box.
        :param bbox: Bounding box of the GeoDataFrame to use.
        :param resolution: "l", "i", "h" ...
        :param proj: "lcc", ...
        :return: A Basemap map object.
        """
        plt.rcParams['figure.figsize'] = (self.map_width, self.map_height)

        map_created = Basemap(llcrnrlon=bbox[0], llcrnrlat=bbox[1],
                              urcrnrlon=bbox[2], urcrnrlat=bbox[3],
                              resolution=resolution, projection=proj,
                              lat_1=bbox[0], lon_0=bbox[2])
        # NOTE: Works but why do we need to project in WGS 84 before?
        # NOTE: Works but don't understand what means lat_1 and lon_0

        return map_created

    def map_background(self, the_map):
        """
        All options here http://matplotlib.org/basemap/api/basemap_api.html
        """
        if self.map_countries is True:
            the_map.drawcountries(linewidth=self.map_countries_boundary_width, color=self.map_countries_boundary_color,
                                  zorder=1)
        if self.map_coastlines is True:
            the_map.drawcoastlines(linewidth=self.map_coastlines_width, color=self.map_coastlines_color,
                                   zorder=1)
        if self.map_fill_continents is True:
            the_map.fillcontinents(color=self.map_continents_color, lake_color=self.map_continents_color_lake,
                                   zorder=0, alpha=self.map_continents_alpha)
        if self.map_shaded_relief is True:
            the_map.shadedrelief(zorder=0, alpha=0.2)

    def show(self, sql, geom_field="geom", column=None, scheme="QUANTILES", k=8, colormap='binary', alpha=0.8,
             o_file=None):
        """
        Uses GeoPandas to show the data. No background but very fast maps.
        Choropleth maps by default.
        """
        plt.rcParams['figure.figsize'] = (self.map_width, self.map_height)

        geo_dataframe = self.db.geo_select(sql, geom_field)
        if column is None:
            alpha = 0.  # NOTE: Choropleth display by default. So alpha is set to zero
            geo_dataframe.plot(colormap=colormap, alpha=alpha)
        else:
            geo_dataframe.plot(colormap=colormap, column=column, scheme=scheme, k=k, alpha=alpha)

        if o_file is None:
            plt.show()
        else:
            plt.savefig(o_file, dpi=self.dpi, bbox_inches='tight')

    def map(self, sql, geom_field="geom", color="black", border_color="black", line_width=1., marker="o", size=18,
            title=u"", resolution="i", proj="lcc", zorder=10, alpha=1., fill=False, o_file=None):
        geo_dataframe = self.db.geo_select(sql, geom_field)
        bbox = calculate_bbox(geo_dataframe)  # In WGS 84
        geom_type = global_geometry_type(geo_dataframe)

        if geom_type == "Point":
            self.map_points(geo_dataframe, bbox, color, marker, size, title, resolution, proj, o_file)
            # NOTE: **kwargs?
        elif geom_type == "Line":
            print "ERROR: Function not already implemented"
        elif geom_type == "Polygon":
            self.map_polygons(geo_dataframe, bbox, title, resolution, proj, color, border_color, zorder, line_width,
                              alpha, fill, o_file)  # NOTE: **kwargs?

    def map_points(self, geo_dataframe, bbox, color, marker, size, title, resolution, proj, o_file):
        the_map = self.map_general(bbox, resolution, proj)  # Creates the map
        self.map_background(the_map)  # Draw map background

        # Plot data
        x_coords, y_coords = extract_points_xy(geo_dataframe, 4326)  # NOTE: Needs to be in wgs84. Why?
        x, y = the_map(x_coords, y_coords)
        the_map.scatter(x, y, size, marker=marker, color=color, zorder=10)

        # Add secondary information
        plt.title(title)

        if o_file is None:
            plt.show()
        else:
            plt.savefig(o_file, dpi=self.dpi, bbox_inches='tight')

    def map_polygons(self, geo_dataframe, bbox, title, resolution, proj, color, border_color, zorder, line_width,
                     alpha, fill, o_file):
        """
        Thanks to IEM Blog for the tip:
        http://iemblog.blogspot.fr/2011/06/simple-postgis-python-ogr-matplotlib.html.
        """
        if geo_dataframe.crs['init'] != "epsg:4326":  # GeoDataFrame must be in WGS84
            geo_dataframe = projection(geo_dataframe, 4326)

        the_map = self.map_general(bbox, resolution, proj)  # Creates the map

        # Create polygons patches
        patches = []
        for obj in geo_dataframe.geometry.values:
            for polygon in obj.geoms:
                # Grab polygon exterior coordinates with numpy.asarray
                a = asarray(polygon.exterior)
                x, y = the_map(a[:, 0], a[:, 1])
                a = zip(x, y)
                p = Polygon(a, fc=color, ec=border_color, zorder=zorder, lw=line_width, alpha=alpha, fill=fill)
                patches.append(p)

        ax = plt.axes([0, 0, 1, 1])
        self.map_background(the_map)
        ax.add_collection(PatchCollection(patches, match_original=True))

        plt.title(title)

        if o_file is None:
            plt.show()
        else:
            plt.savefig(o_file, dpi=self.dpi, bbox_inches='tight')

if __name__ == "__main__":

    import os
    import unittest
    from pg import Pg

    class TestFunctions(unittest.TestCase):

        print "Testing", os.path.basename(__file__)

        def test_pgmap_object_creation(self):
            pm = PgMap("config.cfg")
            self.assertIsInstance(pm.config_file, str)
            self.assertIsInstance(pm.db, Pg)
            self.assertIsInstance(pm.map_width, float)
            self.assertGreaterEqual(pm.map_width, 0.1)
            self.assertIsInstance(pm.map_height, float)
            self.assertGreaterEqual(pm.map_height, 0.1)
            self.assertIsInstance(pm.map_countries, bool)
            self.assertIsInstance(pm.map_countries_boundary_color, str)
            self.assertIsInstance(pm.map_countries_boundary_width, float)
            self.assertIsInstance(pm.map_coastlines, bool)
            self.assertIsInstance(pm.map_coastlines_width, float)
            self.assertIsInstance(pm.map_coastlines_color, str)
            self.assertIsInstance(pm.map_fill_continents, bool)
            self.assertIsInstance(pm.map_coastlines_color, str)
            self.assertIsInstance(pm.map_continents_color, str)
            self.assertIsInstance(pm.map_continents_color_lake, str)
            self.assertIsInstance(pm.map_continents_alpha, float)
            self.assertIsInstance(pm.map_shaded_relief, bool)
            self.assertIsInstance(pm.dpi, int)

        def test_reload_config_file(self):
            pm = PgMap("config.cfg")
            pm.reload_config("config.cfg")
            self.test_pgmap_object_creation()

        def test_map_general(self):
            pm = PgMap("config.cfg")
            pm.map_general([1, 2, 3, 4], "i", "lcc")
            self.assertIsInstance(plt.rcParams['figure.figsize'], list)
            self.assertEqual(len(plt.rcParams['figure.figsize']), 2)
            self.assertIsInstance(plt.rcParams['figure.figsize'][0], float)
            self.assertIsInstance(plt.rcParams['figure.figsize'][1], float)

        def test_map_background(self):
            pass  # TODO: How to do unittests?

        def test_show(self):
            pass  # TODO: How to do unittests?

        def test_map(self):
            pass  # TODO: How to do unittests?

        def test_map_points(self):
            pass  # TODO: How to do unittests?

        def test_map_polygons(self):
            pass  # TODO: How to do unittests?

    unittest.main()

    # pm = PgMap("config.cfg")
    #
    # # Testing show data
    # pm.show("select * from bdcarthage.point_eau_isole;", "the_geom")
    # pm.show("select * from bdcarthage.troncon_hydrographique limit 1000;", "the_geom")
    # pm.show("select * from bdcarthage.secteur;", "the_geom")
    # pm.show("""
    #     select id_geofla, population, the_geom as geom from geofla.commune_50 where code_reg = '93';
    #     """, column="population")
    #
    # Testing show data saving file
    # pm.show("select * from bdcarthage.point_eau_isole;", "the_geom", o_file="aa.png")
    # # Test points with Basemap
    # pm.map("select * from bdcarthage.point_eau_isole;", "the_geom")
    # pm.map("select gid, st_transform(the_geom, 4326) as the_geom from bdcarthage.point_eau_isole;", "the_geom")
    #
    # # Testing points in basemap saving file
    # pm.map("select * from bdcarthage.point_eau_isole;", "the_geom", o_file="bb.png")
    #
    # # Test polygons with Basemap
    # pm.map("select * from bdcarthage.secteur;", "the_geom")
    #
    # # Test special map background
    # pm.map_shaded_relief = False
    # pm.map_fill_continents = True
    # pm.map_continents_alpha = 1.
    # pm.map_continents_color = "green"
    # pm.map_countries_boundary_color = "yellow"
    # pm.map_countries_boundary_width = 3
    # pm.map_coastlines_width = 3
    # pm.map_coastlines_color = "yellow"
    # pm.map("select * from bdcarthage.secteur;", "the_geom", fill=False)