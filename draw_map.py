# -*- coding:utf-8 -*-
# R. Souweine, 2015

# TODO: Be able to plot multiple layers in one basemap plot.
# TODO: Options for map background
# TODO: Plot lines with basemap
# TODO: Unittests

import matplotlib
matplotlib.use("WXagg")  # FIXME: Find platform? http://matplotlib.org/faq/usage_faq.html#what-is-a-backend
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from numpy import asarray
from pg import Pg
from geo_df_utils import calculate_bbox, extract_points_xy, projection, global_geometry_type


class PgMap():
    def __init__(self, config_file):
        self.config_file = config_file
        self.db = Pg(self.config_file)
        self.map_width = 12.0
        self.map_height = 12.0

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

    @staticmethod
    def map_background(the_map):
        the_map.drawcountries(linewidth=0.5, color='grey')
        the_map.drawcoastlines(linewidth=0.5, color='grey')
        the_map.fillcontinents(color='lightgrey', lake_color='white', zorder=1, alpha=0.2)
        the_map.shadedrelief(zorder=0, alpha=0.2)

    @staticmethod
    def show_colormaps():
        print """
        Colormaps for GeoPandas plots - PgMap.show():
        binary
        Blues
        YlOrRd
        ...
        """

    def show(self, sql, geom_field="geom", column=None, scheme="QUANTILES", k=8, colormap='binary', alpha=0.8):
        """
        Uses GeoPandas to show the data. No background but very fast maps.
        Choropleth maps by default.
        """
        self.map_general()

        geo_dataframe = self.db.geo_select(sql, geom_field)
        if column is None:
            alpha = 0.  # NOTE: Choropleth display by default. So alpha is set to zero
            geo_dataframe.plot(colormap=colormap, alpha=alpha)
        else:
            geo_dataframe.plot(colormap=colormap, column=column, scheme=scheme, k=k, alpha=alpha)
        plt.show()

    def map(self, sql, geom_field="geom", color="red", border_color="black", line_width=.2, marker="o", size=18,
            title=u"", resolution="i", proj="lcc", zorder=2, alpha=0.5, fill=True):
        geo_dataframe = self.db.geo_select(sql, geom_field)
        bbox = calculate_bbox(geo_dataframe)  # In WGS 84
        geom_type = global_geometry_type(geo_dataframe)

        if geom_type == "Point":
            self.map_points(geo_dataframe, bbox, color, marker, size, title, resolution, proj)
            # FIXME: Repeated two times kwargs?
        elif geom_type == "Line":
            print "ERROR: Function not already implemented"
        elif geom_type == "Polygon":
            self.map_polygons(geo_dataframe, bbox, title, resolution, proj, color, border_color, line_width, zorder,
                              alpha, fill)
            # FIXME: Repeated two times kwargs?

    def map_points(self, geo_dataframe, bbox, color, marker, size, title, resolution, proj):
        the_map = self.map_general(bbox, resolution, proj)  # Creates the map
        self.map_background(the_map)  # Draw map background

        # Plot data
        x_coords, y_coords = extract_points_xy(geo_dataframe, 4326)  # NOTE: Needs to be in wgs84. Why?
        x, y = the_map(x_coords, y_coords)
        the_map.scatter(x, y, size, marker=marker, color=color, zorder=10)

        # Add secondary information
        plt.title(title)
        plt.show()

    def map_polygons(self, geo_dataframe, bbox, title, resolution, proj, color, border_color, zorder, line_width,
                     alpha, fill):
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
        plt.show()

if __name__ == "__main__":
    pm = PgMap("config.cfg")

    # Testing show data
    # pm.show("select * from bdcarthage.point_eau_isole;", "the_geom")
    # pm.show("select * from bdcarthage.troncon_hydrographique limit 1000;", "the_geom")
    # pm.show("select * from bdcarthage.secteur;", "the_geom")
    # pm.show("""
    #     select id_geofla, population, the_geom as geom from geofla.commune_50 where code_reg = '93';
    #     """, column="population")

    # Test points with Basemap
    # pm.map("select * from bdcarthage.point_eau_isole;", "the_geom")
    # pm.map("select gid, st_transform(the_geom, 4326) as the_geom from bdcarthage.point_eau_isole;", "the_geom")

    # Est polygons with Basemap
    pm.map("select * from bdcarthage.secteur;", "the_geom")