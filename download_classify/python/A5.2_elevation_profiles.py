
#Script for gettign data for elevation profiles (either using existing data with elevation info or creating new points for a route of connecting ways)
# See elevation.sql and elevation_profile.sql for information about the method
#%%
#Importing modules
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from database_functions import *
#%%
# Connecting to database
connection = connect_pg(db_name, db_user, db_password)
#%%
# Experimenting with plotting elevation profiles

#Using points with elevation data created previously (use OSM id to define way)
sql_points = 'SELECT *, ST_X(geom) x, ST_Y(geom) y FROM point_geometries WHERE osm_id = 108849035 ORDER BY path;'
#data = run_query_pg(sql, connection)
elevation_points = gpd.read_postgis(sql_points, connection, geom_col='geom' )
#%%
xline = elevation_points['x']
yline = elevation_points['y']
zline = elevation_points['elevation']

ax = plt.axes(projection='3d')
ax.plot3D(xline, yline, zline, 'gray')
# %%
#Export to csv
elevation_points.to_csv('../data/elevation_profile_1.csv')
# %%
#Creating new elevation points from a selection of ways
#Edit elevation_profile.sql to change which ways are included
create_points = run_query_pg('--/data/elevation_profile.sql', connection)
#%%
elevation_profile = 'SELECT * FROM points;'
ele_data = gpd.read_postgis(elevation_profile, connection, geom_col='geom')
# %%
ele_data.to_csv('../data/elevation_profile_2.csv')
# %%
xline = ele_data['x_coord']
yline = ele_data['y_coord']
zline = ele_data['z_coord']

ax = plt.axes(projection='3d')
ax.plot3D(xline, yline, zline, 'red')
#%%
# If data need to be sorted (i.e. line ids provided in the wrong order)

#ele_data.sort_values(by=['path'], ascending=True, inplace=True)
#ele_data.sort_values(by=['x_coord'], ascending=False, inplace=True)
# %%
