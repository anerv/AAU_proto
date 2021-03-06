'''
This script runs several sql script and files to reclassify the osm data based on the original tags
Unused columns and rows are deleted (but can still be found in the table created from the original osm file)

'''
#%%
#Importing modules
import psycopg2 as pg
from config import *
from database_functions import connect_pg, run_query_pg
import geopandas as gpd

# %%
# Connecting to the database
connection = connect_pg(db_name, db_user, db_password)

#%%
#Delecting unneccessary rows
clear_rows_ways = "DELETE FROM %s WHERE highway IS NULL OR highway IN ('raceway', 'platform')" % ways_table
clear_rows_rel = "DELETE FROM %s WHERE route NOT IN ('fitness_trail' , 'foot' , 'hiking' , 'bicycle', 'road' ) OR route IS NULL" % rel_table

run_clear_w = run_query_pg(clear_rows_ways, connection)
run_clear_rel = run_query_pg(clear_rows_rel, connection)

#%%
#Columns to be dropped from tables

#Columns to be dropped from ways table
ways_col = ['admin_level', 'amenity', 'area', 'boundary', 'harbour', 'horse', 'landuse', '"lanes:backward"', '"lanes:forward"', 'leisure', 'noexit', 'operator', 'railway', 'shop', 'traffic_sign', '"turn:lanes"', '"turn:backward"', '"turn:forward"', 'water', 'waterway', 'wetland', 'wood']
ways_del = ', DROP COLUMN '.join(ways_col)
ways_del = 'ALTER TABLE %s ' % ways_table + 'DROP COLUMN ' + ways_del + ';'

#Columns to be dropped from relations table
rel_useful_cols = ['osm_id', 'name', 'operator','ref','route','geom']
rel_query = "SELECT * FROM %s" % rel_table
relations = gpd.read_postgis(rel_query, connection, geom_col='geom')
rel_org_cols = list(relations.columns)
rel_cols_del = [i for i in rel_org_cols if i not in rel_useful_cols]
rel_del = '", DROP COLUMN "'.join(rel_cols_del)
rel_del = 'ALTER TABLE %s ' % rel_table + 'DROP COLUMN "' + rel_del + '";'

#Columns to be dropped from points table
points_useful_cols = ['osm_id','amenity','area','barrier','bicycle','bollard','crossing','crossing:island','crossing:ref','ele','flashing_lights','foot','highway','layer','lit','parking','public_transport','railway','ref','segregated','service:bicycle:chain_tool','service:bicycle:pump','service','shop','surface','traffic_calming','traffic_sign','traffic_signals','geom']
points_query = "SELECT * FROM %s" % points_table
points = gpd.read_postgis(points_query, connection, geom_col='geom')
points_org_cols = list(points.columns)
points_cols_del = [i for i in points_org_cols if i not in points_useful_cols]
points_del = '", DROP COLUMN "'.join(points_cols_del)
points_del = 'ALTER TABLE %s ' % points_table + 'DROP COLUMN "' + points_del + '";'

#%%
#Deleting unneccessary columns
run_del_w = run_query_pg(ways_del, connection)
run_del_p = run_query_pg(points_del, connection)
run_del_r = run_query_pg(rel_del, connection)

#%%
#Classifying ways table

#Filepath to sql file
fp_ways = '../sql/classify_osm_waystable.sql'

run_class_w = run_query_pg(fp_ways, connection)

#%%
#Classyfing points table

#Filepath to sql file
fp_points =  '../sql/classify_osm_points.sql'

run_class_p = run_query_pg(fp_points, connection)

#%%
#Joining data about cycle routes to ways data

#Filepath to sql file
fp_rel = '../sql/join_relations_to_ways.sql'

run_ways_rel = run_query_pg(fp_rel, connection)

#%%
#Saving bicycle parking and bicycle rental to separate table
poly_service = "CREATE TABLE poly_service AS (SELECT osm_id, amenity, geom FROM %s WHERE amenity IN ('bicycle_parking','bicycle_rental'))" % lu_table
run_poly_service = run_query_pg(poly_service, connection)

#%%
#Creating spatial index for table with cycle services
index_bi_s = "CREATE INDEX b_s_geom_idx ON poly_service USING GIST (geom);"
create_index = run_query_pg(index_bi_s, connection)

#%%
#Adding information about administrative area
run_adm = run_query_pg('../sql/adding_adm_area.sql', connection)
#%%
# Testing the results

#Add here

#%%
#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
