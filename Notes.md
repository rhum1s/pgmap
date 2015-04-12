### Tests relies on my own db. Maybe must create a test db?
### Geometry bounding box of a GeoDataFrame can be obtained from:
```
gdf.geometry.total_bounds
```
### Geometry column name could have been find automatically with GeoDataFrame.geometry.name
* In geo_select(self, sql, geom_col='geom') we rename if needed the geometry field which is not good.