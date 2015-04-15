# -*- coding:utf-8 -*-
# R. Souweine, 2015

import matplotlib
matplotlib.use("WXagg")  # FIXME: Find platform? http://matplotlib.org/faq/usage_faq.html#what-is-a-backend
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
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

    def map_general(self):
        plt.rcParams['figure.figsize'] = (self.map_width, self.map_height)

    @staticmethod
    def map_background(the_map):
        the_map.drawcountries(linewidth=0.5, color='grey')
        the_map.drawcoastlines(linewidth=0.5, color='grey')
        the_map.fillcontinents(color='lightgrey',lake_color='white', zorder=1, alpha=0.2)
        # map.shadedrelief(zorder=0, alpha=0.2)  # FIXME: Doesn't seems to work!

    def map(self, sql, geom_field="geom"):
        geo_dataframe = self.db.geo_select(sql, geom_field)
        bbox = calculate_bbox(geo_dataframe)  # In WGS 84
        geom_type = global_geometry_type(geo_dataframe)

        if geom_type == "Point":
            self.map_points(geo_dataframe, bbox)
        elif geom_type == "Line":
            print "ERROR: Function not already implemented"
        elif geom_type == "Polygon":
            print "ERROR: Function not already implemented"

    def map_points(self, geo_dataframe, bbox):
            self.map_general()  # General map params

            the_map = Basemap(llcrnrlon=bbox[0],
                              llcrnrlat=bbox[1],
                              urcrnrlon=bbox[2],
                              urcrnrlat=bbox[3],
                              resolution='i',
                              projection='lcc',
                              lat_1=bbox[0],
                              lon_0=bbox[2])
            # NOTE: Works but why do we need to project in WGS 84 before?
            # NOTE: Works but don't understand what means lat_1 and lon_0

            self.map_background(the_map)  # Draw map background

            # Plot data
            x_coords, y_coords = extract_points_xy(geo_dataframe, 4326)  # NOTE: Needs to be in wgs84. Why?
            x, y = the_map(x_coords, y_coords)
            the_map.scatter(x, y, 18, marker='o', color='black', zorder=10)

            # Add secondary information
            plt.title('TITRE')
            plt.show()

pm = PgMap("config.cfg")
pm.map("select * from bdcarthage.point_eau_isole;", "the_geom")
# pm.map("select gid, st_transform(the_geom, 4326) as the_geom from bdcarthage.point_eau_isole;", "the_geom")






