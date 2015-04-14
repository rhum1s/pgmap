# -*- coding:utf-8 -*-
# R. Souweine, 2015

import sys


def global_geometry_type(geo_data_frame):
    """
    Three global geometry types: Point, Line, Strings
    :param geo_data_frame: A pandas GeoDataFrame with geometry column named "geom"
    :return: Text.
    """
    if len(geo_data_frame.geom_type.unique()) > 1:
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


def projection(geo_data_frame, to_epsg):
    """
    GeoDataFrame projection.
    - Set default crs
    - Use GeoPandas to transform to another crs.
    - Pass the values of the new geometry field to the old one and delete the new
    - Declare again geometry field.
    :param geo_data_frame: A pandas GeoDataFrame with geometry column named "geom"
    :param to_epsg: Output desired EPSG
    :return: GeoDataFrame
    """
    geo_data_frame_projected = geo_data_frame.to_crs(epsg=to_epsg)
    geo_data_frame_projected.geom = geo_data_frame_projected.geometry
    geo_data_frame_projected.drop('geometry', 1, inplace=True)
    geo_data_frame_projected.set_geometry("geom", inplace=True)

    return geo_data_frame_projected


def calculate_bbox(geo_data_frame):
    """
    :return: A list representing the bounding box
    """
    # TODO: Must project coordinates one by one and not all the dataframe
    bbox = [180, 90, -180, -90]

    geo_data_frame = projection(geo_data_frame, 4326)  # Convert to WGS84
    geo_data_frame_wgs84_bbox = geo_data_frame.total_bounds

    bbox[0] = min(bbox[0], geo_data_frame_wgs84_bbox[0]) - 0.05
    bbox[1] = min(bbox[1], geo_data_frame_wgs84_bbox[1]) - 0.05
    bbox[2] = max(bbox[2], geo_data_frame_wgs84_bbox[2]) + 0.05
    bbox[3] = max(bbox[3], geo_data_frame_wgs84_bbox[3]) + 0.05
    return bbox


if __name__ == "__main__":

    import os
    import unittest
    import numpy as np
    from pg import Pg

    db = Pg("config.cfg")

    class TestFunctionsPg(unittest.TestCase):

        print "Testing", os.path.basename(__file__)

        def test_global_geometry_type(self):
            gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 100;")
            gdf_geometry_type = global_geometry_type(gdf)
            self.assertEqual(gdf_geometry_type, "Line")

        def test_extract_points_xy(self):
            gdf = db.geo_select("select * from bdcarthage.point_eau_isole limit 3;", "the_geom")
            x, y = extract_points_xy(gdf)
            self.assertIsInstance(x, list)
            self.assertIsInstance(y, list)

        def test_projection(self):
            gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 100;")
            gdf = projection(gdf, 4326)
            new_epsg = gdf.crs["init"]
            self.assertEqual(new_epsg, "epsg:4326")

        def test_calculate_bbox(self):
            gdf = db.geo_select("select * from bdcarthage.cours_d_eau limit 100;")
            bbox = calculate_bbox(gdf)
            self.assertIsInstance(bbox, list)
            self.assertEqual(len(bbox), 4)
            self.assertIsInstance(bbox[0], np.float64)
            self.assertIsInstance(bbox[1], np.float64)
            self.assertIsInstance(bbox[2], np.float64)
            self.assertIsInstance(bbox[3], np.float64)
            self.assertLessEqual(bbox[0], 180)  # Is it in WGS84 bounds
            self.assertLessEqual(bbox[1], 90)  # Is it in WGS84 bounds
            self.assertGreaterEqual(bbox[2], -180)  # Is it in WGS84 bounds
            self.assertGreaterEqual(bbox[2], -90)  # Is it in WGS84 bounds

    unittest.main()