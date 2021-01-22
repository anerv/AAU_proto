#Save tables to file (either Shape or Geopackage)
# Must be adapted to include traffic counts and noise variables
#%%
#Importing modules
from config import *
from database_functions import run_query_pg, connect_pg, connect_alc, to_postgis
import geopandas as gpd
import pandas as pd
#%%
#Connecting to database
connection = connect_pg(db_name, db_user, db_password)
# %%
#Retrieving data from database
retrieve_ways = "SELECT * FROM %s;" % ways_table
retrieve_points_s = "SELECT * FROM points_service;"
retrieve_points_i = "SELECT * FROM points_infra;"
retrieve_poly_s = "SELECT * FROM poly_service;"
retrieve_traffic = "SELECT * FROM traffic_counts;"
#%%
#Loading data to geodataframes
ways_gdf = gpd.GeoDataFrame.from_postgis(retrieve_ways, connection, geom_col='geom')
points_s_gdf = gpd.GeoDataFrame.from_postgis(retrieve_points_s, connection, geom_col='geom')
points_i_gdf = gpd.GeoDataFrame.from_postgis(retrieve_points_i, connection, geom_col='geom')
poly_service = gpd.GeoDataFrame.from_postgis(retrieve_poly_s, connection, geom_col='geom')
traffic_counts_gdf = gpd.GeoDataFrame.from_postgis(retrieve_traffic, connection, geom_col='geom')
# %%
'''
#Get test data instead of entire ways table
get_test = "SELECT * FROM test;"
ways_gdf = gpd.GeoDataFrame.from_postgis(get_test, connection, geom_col='geom')
'''
#%%
#Saving tables to geopackage
#Drop columns to simplify file
drop_cols = ['flashing_lights','maxspeed:advisory','moped','motorcar','motor_vehicle','parking:lane','parking:lane:right','parking:lane:left','parking:lane:both','public_transport','ref','service','source:maxspeed','z_order','way_area']
ways_gdf.drop(columns=drop_cols, inplace=True)

fp_gpkg = '..\\data\\' + 'cycling_infra_2.gpkg'

ways_gdf.to_file(fp_gpkg, layer=ways_table, driver="GPKG")
points_s_gdf.to_file(fp_gpkg, layer='points_service', driver="GPKG")
points_i_gdf.to_file(fp_gpkg, layer='points_infra', driver="GPKG")
poly_service.to_file(fp_gpkg, layer='poly_service', driver="GPKG")

#%%
'''
#If a shapefile is needed:
#Renaming column names to be compatible with shapefile limitations
ways_dict = {'cycleway:left':'c_w_left', 'cycleway:right':'c_w_r', 'cycleway:width':'c_width', 'cycleway:left:width':'c_l_width', 'cycleway:right:width':'c_r_width', 'cycleway:both:width':'c_b_width', 'cycleway:surface':'c_surface', 'maxspeed:advisory':'maxs_advised', 'motor_vehicle':'motorveh.', 'oneway_bicycle':'onewaybike', 'parking:lane':'p_lane','parking:lane:right':'p_lane_r','parking:lane:left':'p_lane_l','parking:lane:both':'p_l_both','public_transport':'p_trans','car_traffic':'cartraff.','cycling_infrastructure':'c_infra','cycling_infra_simple':'c_infra_s','along_street':'by_street','cy_infra_separated':'cycle_sep','cycling_friendly':'c_friendly','cycling_allowed':'c_allowed','cycling_against':'c_against','pedestrian_allowed':'ped_yes','on_street_park':'parking','surface_assumed':'surface2'}
ways_gdf2 = ways_gdf.rename(columns=ways_dict, inplace = False)

#Drop columns to simplify file
drop_cols_shape = ['flashing_lights','maxs_advised','moped','motorcar','motorveh.','p_lane','p_lane_r','p_lane_l','p_l_both','p_trans','ref','service','source:maxspeed','z_order','way_area']
ways_gdf2.drop(columns=drop_cols_shape, inplace=True)
#%%
#Saving tables to shapefile
fp_ways = '..\\data\\' + ways_table + '.shp'
fp_points_i = '..\\data\\' + 'points_infra.shp'
fp_points_s = '..\\data\\' + 'points_service.shp'

ways_gdf2.to_file(fp_ways)
points_i_gdf.to_file(fp_points_i)
points_s_gdf.to_file(fp_points_s)
'''
#%%
#Saving tables to csv

#First, convert geom to lat long (lines and polygons are converted to centroids)
convert_geom_latlong = run_query_pg('../sql/convert_geom_to_latlong.sql', connection)
#%%
#If geometries are neede as WKT
convert_geom_wkt = run_query_pg('../sql/geom_to_wkt.sql',connection)
#%%
#Copying geodataframes
ways_latlong = ways_gdf.copy(deep=True)
servicepoints_latlong = points_s_gdf.copy(deep=True)
serviceinfra_latlong = points_i_gdf.copy(deep=True)
servicepoly_latlong = poly_service.copy(deep=True)

#%%
#Drop columns from way data to simplify file (including geom)
drop_cols_cent = ['geom', 'flashing_lights','maxspeed:advisory','moped','motorcar','motor_vehicle','parking:lane','parking:lane:right','parking:lane:left','parking:lane:both','public_transport','ref','service','source:maxspeed','z_order','way_area']
ways_latlong.drop(columns=drop_cols_cent, inplace=True)

#Drop geom column from other geodataframes
servicepoints_latlong.drop(columns='geom',inplace=True)
serviceinfra_latlong.drop(columns='geom',inplace=True)
servicepoly_latlong.drop(columns='geom',inplace=True)
# %%
#Convert to regular dataframe to enable saving to csv
ways_latlong.to_csv('../data/ways_latlong.csv')
serviceinfra_latlong.to_csv('../data/service_infra_latlong.csv')
servicepoints_latlong.to_csv('../data/service_points_latlong.csv')
servicepoly_latlong.to_csv('../data/service_poly_latlong.csv')
# %%
