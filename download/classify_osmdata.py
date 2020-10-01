'''
This script reclassifies the original OSM data 
'''
#%%
#Importing modules
from config_download import crs, db_user, db_password, db_host, database_name, db_port
import psycopg2 as pg
import pandas as pd
import geopandas as gpd

#%%
#Connecting to database and creating cursor for queries
try:
    connection = pg.connect(database = database_name, user = db_user,
                                  password = db_password,
                                  host = db_host)

    print("You are connected to the database!","\n")

except (Exception, pg.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

#%%
# Test if you can retrieve data from the database
cursor = connection.cursor()
sql = "SELECT osmid, cycleway, highway, geometry FROM osmways"
try:
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in range(5):
        print('Row number %d :\n' % (row), rows[row]) 
except(Exception, pg.Error) as error:
    print(error)
#%%
# Testing reading data into dataframe
try:
    data = gpd.read_postgis(sql, connection, geom_col='geometry')
    print('The query can also be loaded into a geopandas dataframe:\n', data.head())
except(Exception) as error:
    print(error)
# %%

# %%
