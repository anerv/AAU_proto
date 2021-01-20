'''
This scripts calculates the elevation profile for cycling infrastructure based on a DEM
The method uses a DEM with an optional resolution
The raster is loaded to the database using raster2pgsql, but use the code below to check that the raster has the correct format
'''

#%%
#Importing modules
import rasterio
from rasterio.enums import Resampling
from config import *
from database_functions import *
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
#%%
# %%
# Read raster
dem = rasterio.open(fp_dem)
#%%
#Check crs
if dem.crs == crs:
    print('The DEM is in the right projection')
else:
    print('Please reproject DEM to EPSG:%d' % crs)
# %%
# Connecting to database
connection = connect_pg(db_name, db_user, db_password)
#%%
#Running script assigning elevation to way vertices and computing slope for ways
run_elevation_script = run_query_pg('../sql/elevation.sql', connection)
# %%
# Experimenting with plotting elevation profiles

#Select way
sql = 'SELECT *, ST_X(geom) x, ST_Y(geom) y FROM point_geometries WHERE osm_id = 108849035 ORDER BY path;'
#data = run_query_pg(sql, connection)
data = gpd.read_postgis(sql, connection, geom_col='geom' )
#%%
xline = data['x']
yline = data['y']
zline = data['elevation']

ax = plt.axes(projection='3d')
ax.plot3D(xline, yline, zline, 'gray')
# %%
#Export to csv
data_pd.to_csv('../data/ele_profile.csv')
# %%
