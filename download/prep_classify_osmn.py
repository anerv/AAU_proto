'''
This script reclassifies the original OSM data for data downloaded using osmnx and a predefined study area
'''
#%%
#Importing modules
from config_download import *
import psycopg2 as pg
import geopandas as gpd

#%%
#Setting table names
ways_table = "osmways" + area_name
nodes_table = "osmnodes" + area_name
sa_table = "study_area" + area_name
print('Table names are:', ways_table, nodes_table, sa_table)
#%%

#Connecting to database 
try:
    connection = pg.connect(database = database_name, user = db_user,
                                  password = db_password,
                                  host = db_host)

    print('You are connected to the database %s!' % database_name)

except (Exception, pg.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

#%%
# Test if you can retrieve data from the database
cursor = connection.cursor()
sql_ways = "SELECT osmid, cycleway, highway, geometry FROM %s" % ways_table
sql_nodes = "SELECT osmid, geometry FROM %s" % nodes_table
sql_sa = "SELECT* FROM %s" %sa_table


try:
    cursor.execute(sql_ways)
    rows = cursor.fetchall()
    for row in range(5):
        print('Row number %d :\n' % (row), rows[row]) 
except(Exception, pg.Error) as error:
    print(error)
#%%
#Testing reading data into dataframe
try:
    data = gpd.read_postgis(sql_ways, connection, geom_col='geometry')
    print('The query can also be loaded into a geopandas dataframe:\n', data.head())
except(Exception) as error:
    print(error)
# %%
#Reprojecting data
sql_transform1 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (ways_table, crs, crs)

sql_transform2 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(POINT,%d) USING ST_Transform(geometry,%d)" % (nodes_table, crs, crs)

sql_transform3 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(MULTIPOLYGON,%d) USING ST_Transform(geometry,%d)" % (sa_table, crs, crs)

try:
    cursor.execute(sql_transform1)
    ways = gpd.read_postgis(sql_ways, connection, geom_col='geometry')
    print('The crs for ways data is now', ways.crs)
    cursor.execute(sql_transform2)
    nodes = gpd.read_postgis(sql_nodes, connection, geom_col='geometry')
    print('The crs for nodes data is now', nodes.crs)
    cursor.execute(sql_transform3)
    sa = gpd.read_postgis(sql_nodes, connection, geom_col='geometry')
    print('The crs for study area data is now', sa.crs)
except(Exception) as error:
    print(error)
#%%
#Clipping data to study area
clip_ways = "DELETE FROM %s AS ways USING %s AS boundary WHERE NOT ST_DWithin(ways.geometry, boundary.geometry, %d) AND NOT ST_Intersects(ways.geometry, boundary.geometry);" % (ways_table, sa_table, buffer)
clip_nodes = "DELETE FROM %s AS nodes USING %s AS boundary WHERE NOT ST_DWithin(nodes.geometry, boundary.geometry, %d) AND NOT ST_Intersects(nodes.geometry, boundary.geometry);" % (nodes_table, sa_table, buffer)

try:
    cursor.execute(clip_ways)
    print('The ways dataset have been clipped!')
    cursor.execute(clip_nodes)
    print('The nodes dataset have been clipped!')
except(Exception) as error:
    print(error)

#%%
#Commiting changes
connection.commit()
#%%
#Check what clipped data looks like
ways = gpd.read_postgis(sql_ways, connection, geom_col='geometry')
ways.plot()
#%%
sql_file = open('classify_osm_waystable.sql','r')
cursor = connection.cursor()

try:
    cursor.execute(sql_file.read())
except(Exception) as error:
    print(error)
    print('Reconnecting to the database. Please fix error before rerunning')
    connection.close()
    try:
        connection = pg.connect(database = database_name, user = db_user,
                                    password = db_password,
                                    host = db_host)

        print('You are connected to the database %s!' % database_name)

    except (Exception, pg.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    
#%%
#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
