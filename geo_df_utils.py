# -*- coding:utf-8 -*-
# R. Souweine, 2015

import sys


def global_geometry_type(geo_data_frame):
    """
    Three global geometry types: Point, Line, Strings
    :param geo_data_frame: A pandas GeoDataFrame with geometry column named "geom"
    :return: Text.
    """
    if len(gdf.geom_type.unique()) > 1:
        sys.exit("ERROR: There are multiple geometries in the GeoDataFrame")

    geom_type = geo_data_frame.geom_type.unique()[0]
    if geom_type in ("LineString", "MultiLineString"):
        return "Line"
    elif geom_type in ("Point",):
        return "Point"
    elif geom_type in ("Polygon", "MultiPolygon"):
        return "Polygon"
    else:
        sys.exit("ERROR: Geometry type unknown: %s" % geom_type)


def extract_points_xy(geo_data_frame):
    """
    Very useful to work with Matplotlib / Basemap.
    :param geo_data_frame: A pandas GeoDataFrame with geometry column named "geom"
    :return: X list, Y list.
    """
    if global_geometry_type(geo_data_frame) != "Point":
        sys.exit("ERROR: Function extract_points_xy(geo_data_frame) only works with Points.")

    def getx(pt):
        return pt.coords[0][0]

    def gety(pt):
        return pt.coords[0][1]

    x = list(geo_data_frame.geometry.apply(getx))
    y = list(geo_data_frame.geometry.apply(gety))

    return x, y


def projection(geo_data_frame, from_epsg, to_epsg):
    """
    GeoDataFrame projection.
    - Set default crs
    - Use GeoPandas to transform to another crs.
    - Pass the values of the new geometry field to the old one and delete the new
    - Declare again geometry field.
    :param geo_data_frame: A pandas GeoDataFrame with geometry column named "geom"
    :param from_epsg: Input EPSG
    :param to_epsg: Output desired EPSG
    :return: GeoDataFrame
    """
    geo_data_frame.crs = {'init': 'epsg:%s' % from_epsg, 'no_defs': True}
    geo_data_frame_projected = geo_data_frame.to_crs(epsg=to_epsg)
    geo_data_frame_projected.geom = geo_data_frame_projected.geometry
    geo_data_frame_projected.drop('geometry', 1, inplace=True)
    geo_data_frame_projected.set_geometry("geom", inplace=True)

    return geo_data_frame_projected


if __name__ == "__main__":

    from pg import Pg

    db = Pg("config.cfg")
    gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 100;")
    print global_geometry_type(gdf)