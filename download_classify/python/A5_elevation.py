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
#%%