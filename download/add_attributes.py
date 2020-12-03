'''
This script adds additional attributes to ways table.
The data added here are information about street lights and traffic counts but can be replaced with other point data
'''
#%%
#Importing modules
import psycopg2 as pg
from config_download import *
from database_functions import connect_pg, run_query_pg
import sqlalchemy
import geopandas as gpd
#%%
#Load data to database
# Creating engine to connect to database
engine_info = 'postgresql://' + db_user +':'+ db_password + '@' + db_host + ':' + db_port + '/' + db_name

#Connecting to database
try:
    engine = sqlalchemy.create_engine(engine_info)
    engine.connect()
    print('You are connected to the database %s!' % db_name)
except(Exception, sqlalchemy.exc.OperationalError) as error:
    print('Error while connecting to the dabase!', error)

#%%
#File paths to data
light_fp = r'C:\Users\OA03FG\OneDrive - Aalborg Universitet\AAU DATA\AAU GeoDATA\armaturer\Armaturer.shp'
traffic_fp = r'C:\Users\OA03FG\OneDrive - Aalborg Universitet\AAU DATA\AAU GeoDATA\mastra_trafiktaelling.shp'

#Read data
lights = gpd.read_file(light_fp)
traffic = gpd.read_file(traffic_fp)

#%%
#Loading data to database
#Name of tables
table_light = 'street_light'
table_traffic = 'traffic_counts'
#%%

try:
    lights.to_postgis(table_light, engine, if_exists='replace')
    print(table_light, 'successfully loaded to database!')
except(Exception) as error:
    print('Error while uploading data to database:', error)

try:
    traffic.to_postgis(table_traffic, engine, if_exists='replace')
    print(table_traffic, 'successfully loaded to database!')
except(Exception) as error:
    print('Error while uploading data to database:', error)

#%%
#Connecting to database using psycopg2
connection = connect_pg(db_name, db_user, db_password, db_host)
#%%
#Check that data are in the right projection
get_crs_light = "SELECT find_SRID('public', '%s', 'geometry');" % table_light
check_crs_light = run_query_pg(get_crs_light, connection)

if check_crs_light[0][0] != crs:

    #Reproject
    reproj_light = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (table_light, crs, crs)
    reproject1 = run_query_pg(reproj_light,connection,success='Data reprojected')
    
#%%
get_crs_traffic = "SELECT find_SRID('public', '%s', 'geometry');" % table_traffic
check_crs_traffic = run_query_pg(get_crs_traffic, connection)

if check_crs_traffic[0][0] != crs:
    reproj_traffic = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(POINT,%d) USING ST_Transform(geometry,%d)" % (table_traffic, crs, crs)
    reproject2 = run_query_pg(reproj_traffic,connection,success='Data reprojected')

#%%
#Create spatial index
create_index_light = 'CREATE INDEX light_geom_idx ON street_light USING GIST (geometry);'
index_light = run_query_pg(create_index_light,connection)
index_traffic = run_query_pg('CREATE INDEX counts_geom_idx ON traffic_counts USING GIST (geometry);',connection)

#%%
#Join traffic lights to nearest way
join_lights = run_query_pg('nearest_line_from_light.sql',connection)

#Join traffic counts to nearest way
join_traffic = run_query_pg('nearest_line_from_traffic_count.sql',connection)
# %%
