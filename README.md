# pgmap
Plot maps from PostgreSQL queries.    

_Romain Souweine, 2015._   

This script was written to improve my Python knowledge. It doesn't claim to do miraculous things.   
It uses lot of libraries like GeoPandas, Matplotlib, ... Thanks to their authors.      
Required packages has intentionally not been packed in this setup as I think it's quite intrusive for the user (note that it's my first Python packaging so maybe I misunderstood something).   
[unittest, matplotlib, mpl_toolkits.basemap, numpy, psycopg2, pandas, geopandas]   

Usage:   
First Create a config file from config.cfg.example  
```
pm = PgMap("config.cfg")

# Quick plot with no background plots
pm.show("select * from schema.geo_table;") 
# Can include geometry field name and output file to save plot.

# Plot with background using Basemap
pm.map("select * from schema.geo_table;")

# Modify map background characteristics
pm.map_shaded_relief = False
pm.map_fill_continents = True
pm.map_continents_alpha = 1.
pm.map_continents_color = "green"
pm.map_countries_boundary_color = "yellow"
pm.map_countries_boundary_width = 3
pm.map_coastlines_width = 3
pm.map_coastlines_color = "yellow"
pm.map("select * from schema.geo_table;", "the_geom", fill=False)
```
