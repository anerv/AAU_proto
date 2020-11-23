'''
This script classifies osm data downloaded using osm2pgsql
'''
#%%
#Importing modules
from config_download import *
import psycopg2 as pg
import geopandas as gpd
#%%
#Connecting to database and creating cursor for queries
try:
    connection = pg.connect(database = database_name, user = db_user,
                                  password = db_password,
                                  host = db_host)

    print('You are connected to the database %s!' % database_name)

except (Exception, pg.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
# %%
'''
TO DO

- reproject data
- kopier table line og omdøb til ways_table....
- kopier table line og omdøb til relations_table...
- kopier table points og omdøb til....
- load study_area til database og klip data (Evt.)
- tjek at alle har samme CRS
- slet relations fra line data og line data fra relations data
- slet unødvendige kolonner fra ways, relations, points
- klassificer ways
- klassificer
'''
#%%
#Loading study area to database


#Reprojecting data


#Setting table names
ways_table = "ways" + area_name
points_table = "points" + area_name
rel_table = "rel" + area_name
sa_table = "study_area" + area_name
print('Table names are:', ways_table, points_table, sa_table)