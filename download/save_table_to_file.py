#Save tables to file
#%%
#Importing modules
from config_download import *
from database_functions import run_query_pg, connect_pg, connect_alc, to_postgis
import geopandas as gpd 
#%%
#Connecting to database
connection = connect_pg(db_name, db_user, db_password)
# %%
#Retrieving data from database
retrieve_ways = "SELECT * FROM %s;" % ways_table
retrieve_points_s = "SELECT * FROM points_service;"
retrieve_points_i = "SELECT * FROM points_infra;"

ways_gdf = gpd.GeoDataFrame.from_postgis(retrieve_ways, connection, geom_col='geometry')
points_s_gdf = gpd.GeoDataFrame.from_postgis(retrieve_points_s, connection, geom_col='geometry')
points_i_gdf = gpd.GeoDataFrame.from_postgis(retrieve_points_i, connection, geom_col='geometry')
# %%
#Saving tables to geopackage
ways_gdf.to_file("cycling_infra.gpkg", layer=ways_table, driver="GPKG")
#%%
points_s_gdf.to_file("points.gpkg", layer='points_service', driver="GPKG")
points_i_gdf.to_file("points.gpkg", layer='points_infra', driver="GPKG")
# %%
#Saving tables to shapefile
ways_gdf.to_file("%s.shp" % ways_table)
points_s_gdf.to_file('points_service.shp')
points_i_gdf.to_file('points_infra.shp')
# %%
