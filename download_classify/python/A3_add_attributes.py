'''
This script adds additional attributes to ways table.
The data added here are information about street lights and traffic counts but can be replaced with other point data
'''
#%%
#Importing modules
import psycopg2 as pg
from config import *
from database_functions import connect_pg, run_query_pg, connect_alc, to_postgis
import sqlalchemy
import geopandas as gpd
#%%
#Connecting to database
engine = connect_alc(db_name, db_user, db_password)

#%%
#File paths to data
light_fp = '../data/armaturer/Armaturer.shp'
traffic_fp = '../data/mastra_trafiktaelling.shp'
noise_fp = '../data/OPEN_DATA_STOEJDATA_VIEWPoint.shp'

#Read data
lights = gpd.read_file(light_fp)
traffic = gpd.read_file(traffic_fp)
noise = gpd.read_file(noise_fp)

#%%
#Loading data to database

#Name of tables
table_light = 'street_light'
table_traffic = 'traffic_counts'
table_noise = 'noise_variables'

to_postgis(lights, table_light, engine, if_exists='fail')
to_postgis(traffic, table_traffic, engine, if_exists='fail')
to_postgis(noise, table_noise, engine, if_exists = 'fail')

#%%
#Connecting to database using psycopg2
connection = connect_pg(db_name, db_user, db_password, db_host)
#%%
#Rename geometry columns
rename_lights = run_query_pg('ALTER TABLE %s RENAME COLUMN geometry TO geom;' % table_light, connection)
rename_traffic = run_query_pg('ALTER TABLE %s RENAME COLUMN geometry TO geom;' % table_traffic, connection)
rename_noise = run_query_pg('ALTER TABLE %s RENAME COLUMN geometry TO geom;' % table_noise, connection)
#%%
#Check that data are in the right projection
get_crs_light = "SELECT find_SRID('public', '%s', 'geom');" % table_light
check_crs_light = run_query_pg(get_crs_light, connection)

if check_crs_light[0][0] == 0:
    print('Dataset has no or an unknown SRID. Please define the projection')

if check_crs_light[0][0] != crs:

    #Reproject
    reproj_light = "ALTER TABLE %s ALTER COLUMN geom TYPE geometry(POINT,%d) USING ST_Transform(geom,%d)" % (table_light, crs, crs)
    reproject1 = run_query_pg(reproj_light,connection,success='Data reprojected')
else:
    print('Data is in the right projection')  
#%%
#Setting crs
set_srid = run_query_pg('ALTER TABLE %s ALTER COLUMN geom TYPE geometry(POINT, %d) USING ST_SetSRID(geom,25832);' % (table_light, crs), connection)

#%%
#%%
get_crs_traffic = "SELECT find_SRID('public', '%s', 'geom');" % table_traffic
check_crs_traffic = run_query_pg(get_crs_traffic, connection)

if check_crs_traffic[0][0] == 0:
    print('Dataset has no or an unknown SRID. Please define the projection')


if check_crs_traffic[0][0] != crs:
    reproj_traffic = "ALTER TABLE %s ALTER COLUMN geom TYPE geometry(POINT,%d) USING ST_Transform(geom,%d)" % (table_traffic, crs, crs)
    reproject2 = run_query_pg(reproj_traffic,connection,success='Data reprojected')
else:
    print('Data is in the right projection')
#%%
get_crs_noise = "SELECT find_SRID('public', '%s', 'geom');" % table_noise
check_crs_noise = run_query_pg(get_crs_noise, connection)

if check_crs_noise[0][0] == 0:
    print('Dataset has no or an unknown SRID. Please define the projection')


if check_crs_noise[0][0] != crs:
    reproj_noise = "ALTER TABLE %s ALTER COLUMN geom TYPE geom(POINT,%d) USING ST_Transform(geom,%d)" % (table_noise, crs, crs)
    reproject3 = run_query_pg(reproj_noise,connection,success='Data reprojected')
else:
    print('Data is in the right projection')

#%%
#Create spatial index
index_light = run_query_pg('CREATE INDEX light_geom_idx ON street_light USING GIST (geom);',connection)
index_traffic = run_query_pg('CREATE INDEX counts_geom_idx ON traffic_counts USING GIST (geom);',connection)
index_noise = run_query_pg('CREATE INDEX noise_geom_idx ON noise_variables USING GIST(geom);', connection)
#%%
#Join traffic lights and traffic counts to nearest way
fp_l = '../sql/nearest_line_from_light.sql'
fp_t = '../sql/nearest_line_from_traffic_count.sql'

join_lights = run_query_pg(fp_l, connection)
join_traffic = run_query_pg(fp_t,connection)

# %%
# Create reference between noise data and ways
create_ref = run_query_pg('../sql/noise_data.sql', connection, close=True)
#%%