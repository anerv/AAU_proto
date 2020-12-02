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
light_fp =
traffic_fp = 

#Read data
lights = gpd.read_file(light_fp)
traffic = gpd.read_file(traffic_fp)

#Loading data to database
table_light = 'street_light'
table_traffic = 'traffic_counts'

try:
    table_light.to_postgis(table_light, engine, if_exists='replace')
    print(table_light, 'successfully loaded to database!')
except(Exception) as error:
    print('Error while uploading study area data to database:', error)

try:
    table_light.to_postgis(table_traffic, engine, if_exists='replace')
    print(table_traffic, 'successfully loaded to database!')
except(Exception) as error:
    print('Error while uploading study area data to database:', error)

#%%
#Reproject

#Create spatial index

#Join traffic lights to nearest way
SELECT DISTINCT ON (p.osm_id)
    p.osm_id AS point, w.name AS closest_way, ST_Distance(p.geometry,w.geometry) AS dist 
    FROM points_infra AS p
    LEFT JOIN wayskbh AS W ON ST_DWithin(p.geometry,w.geometry,5)
    ORDER BY p.osm_id, dist;

#Join traffic counts to nearest way