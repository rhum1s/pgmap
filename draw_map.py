# -*- coding:utf-8 -*-
# R. Souweine, 2015
"""
Create an object "draw_map" on module load containing params which then can be changed
and all needed functions which can be loaded.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from pg import Pg
from geo_df_utils import calculate_bbox, extract_points_xy, projection


class PgMap():
    def __init__(self, config_file):
        self.config_file = config_file
        self.map_width = 12.0
        self.map_height = 12.0

        self.db = Pg(self.config_file)  # TODO: Function to reload db connection  with new config file

    def map(self, sql, geom_field="geom"):
        geo_dataframe = self.db.geo_select(sql, geom_field)

        # Extent in WGS 84
        bbox = calculate_bbox(geo_dataframe)

        # X/Y coordinates in wgs 84
        geo_dataframe = projection(geo_dataframe, 4326)  # FIXME: Needs to be in wgs84 ??? Why?
        x_coords, y_coords = extract_points_xy(geo_dataframe)  # TODO: Directly add option to extract it as wgs84 in function?

        # Defines plot general vars
        plt.rcParams['figure.figsize'] = (self.map_width, self.map_height)

        # Create the map
        the_map = Basemap(llcrnrlon=bbox[0],llcrnrlat=bbox[1],urcrnrlon=bbox[2],urcrnrlat=bbox[3], resolution = 'i', projection='lcc', lat_1=bbox[0], lon_0=bbox[2])  # NOTE: Wors but why do we need to project in WGS 84 before? And what values to insert in lat0 lon0?

        # Draw map background
        the_map.drawcountries(linewidth=0.5, color='grey')
        the_map.drawcoastlines(linewidth=0.5, color='grey')
        the_map.fillcontinents(color='lightgrey',lake_color='white', zorder=1, alpha=0.2)
        # map.shadedrelief(zorder=0, alpha=0.2)  # TODO: Doesn't seems to work over network

        # Plot data
        x, y = the_map(x_coords, y_coords)
        the_map.scatter(x, y, 18, marker='o', color='black', zorder=10)

        # Add secondary information
        plt.title('Stations METAR')

        # Display or save the map
        plt.show()

pm = PgMap("config.cfg")
pm.map("select * from bdcarthage.point_eau_isole limit 50;", "the_geom")

#
# def draw_map(config_file, sql, geom_field="geom"):
#
#         # Defines default map size
#         map_width = 12.0
#         map_height = 12.0
#
#         # Execute query
#         database = Pg(config_file)
#         geo_dataframe = database.geo_select(sql, geom_field)
#
#         # Extent in WGS 84
#         bbox = calculate_bbox(geo_dataframe)
#
#         # X/Y coordinates in wgs 84
#         geo_dataframe = projection(geo_dataframe, 4326)  # FIXME: Needs to be in wgs84 ??? Why?
#         x_coords, y_coords = extract_points_xy(geo_dataframe)  # TODO: Directly add option to extract it as wgs84 in function?
#
#         # Defines plot general vars
#         plt.rcParams['figure.figsize'] = (map_width, map_height)
#
#         # Create the map
#         the_map = Basemap(llcrnrlon=bbox[0],llcrnrlat=bbox[1],urcrnrlon=bbox[2],urcrnrlat=bbox[3], resolution = 'i', projection='lcc', lat_1=bbox[0], lon_0=bbox[2])  # NOTE: Wors but why do we need to project in WGS 84 before? And what values to insert in lat0 lon0?
#
#         # Draw map background
#         the_map.drawcountries(linewidth=0.5, color='grey')
#         the_map.drawcoastlines(linewidth=0.5, color='grey')
#         the_map.fillcontinents(color='lightgrey',lake_color='white', zorder=1, alpha=0.2)
#         # map.shadedrelief(zorder=0, alpha=0.2)  # TODO: Doesn't seems to work over network
#
#         # Plot data
#         x, y = the_map(x_coords, y_coords)
#         the_map.scatter(x, y, 18, marker='o', color='black', zorder=10)
#
#         # Add secondary information
#         plt.title('Stations METAR')
#
#         # Display or save the map
#         plt.show()
#
#
# draw_map("config.cfg", "select * from bdcarthage.point_eau_isole limit 50;", "the_geom")






