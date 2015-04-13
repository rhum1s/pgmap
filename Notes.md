### Tests relies on my own db. Maybe must create a test db?
### Geometry bounding box of a GeoDataFrame can be obtained from:
```
gdf.geometry.total_bounds
```
### Geometry column name could have been find automatically with GeoDataFrame.geometry.name
* In geo_select(self, sql, geom_col='geom') we rename if needed the geometry field which is not good.
* It can be very complicated to modify query to rename field 
* -> Was a good solution.
### Dataframe EPSG
* Maybe find EPSG on dataframe loading (geo_select()) 
* Define it with gdf.crs = {'init': 'epsg:XXXX', 'no_defs': True}
* And we do not need to define it when re-projecting (projection())
* Problem: If this is  sub query? We can't find it's projection in the database.