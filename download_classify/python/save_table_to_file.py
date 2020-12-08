#Save tables to file
#%%
#Importing modules
from config import *
from database_functions import run_query_pg, connect_pg, connect_alc, to_postgis
import geopandas as gpd
from pathlib import Path
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
#ways_gdf.to_file("cycling_infra.gpkg", layer=ways_table, driver="GPKG")
#points_s_gdf.to_file("points.gpkg", layer='points_service', driver="GPKG")
#points_i_gdf.to_file("points.gpkg", layer='points_infra', driver="GPKG")

# %%
#Renaming column names to be compatible with shapefile limitations
ways_dict = {'cycleway:left':'c_w_left', 'cycleway:right':'c_w_r', 'cycleway:width':'c_width', 'cycleway:left:width':'c_l_width', 'cycleway:right:width':'c_r_width', 'cycleway:both:width':'c_b_width', 'cycleway:surface':'c_surface', 'maxspeed_advisory':'maxs_advised', 'motor_vehicle':'motorveh.', 'oneway_bicycle':'onewaybike', 'parking:lane':'p_lane','parking:lane:right':'p_lane_r','parking:lane:left':'p_lane_l','parking:lane:both':'p_l_both','public_transport':'p_trans','car_traffic':'cartraff.','cycling_infrastructure':'c_infra','cycling_infra_simple':'c_infra_s','along_street':'by_street','cy_infra_separated':'cycle_sep','cycling_friendly':'c_friendly','cycling_allowed':'c_allowed','cycling_against':'c_against','on_street_parking':'parking','surface_assumed':'surface2'}
ways_gdf2 = ways_gdf.rename(columns=ways_dict, inplace = False)

# %%
#Saving tables to shapefile
two_levels_up = str(Path(__file__).parents[1])
fp_ways = two_levels_up + '\\data\\' + ways_table + '.shp'
fp_points_i = two_levels_up + '\\data\\' + 'points_infra.shp'
fp_points_s = two_levels_up + '\\data\\' + 'points_service.shp'
#%%
ways_gdf2.to_file(fp_ways)
#%%
points_i_gdf.to_file(fp_points_i)
points_s_gdf.to_file(fp_points_s)
