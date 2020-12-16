'''
This script reclassifies the original OSM data for data downloaded using osmnx and a predefined study area
'''
#%%
#Importing modules
from config import *
import psycopg2 as pg
import geopandas as gpd
from database_functions import connect_pg, run_query_pg
#%%
#Checking table names
print('Table names are:', ways_table, points_table, sa_table)
#%%

#Connecting to database 
connection = connect_pg(db_name, db_user, db_password)

#%%
# Test if you can retrieve data from the database
cursor = connection.cursor()
sql_ways = "SELECT osm_id, cycleway, highway, geometry FROM %s" % ways_table

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

sql_transform2 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(POINT,%d) USING ST_Transform(geometry,%d)" % (points_table, crs, crs)

sql_transform3 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(MULTIPOLYGON,%d) USING ST_Transform(geometry,%d)" % (sa_table, crs, crs)

reproject_ways = run_query_pg(sql_transform1, connection)
reproject_points = run_query_pg(sql_transform2, connection)
reproject_sa = run_query_pg(sql_transform3, connection)

#%%
#Clipping data to study area
clip_ways = "DELETE FROM %s AS ways USING %s AS boundary WHERE NOT ST_DWithin(ways.geometry, boundary.geometry, %d) AND NOT ST_Intersects(ways.geometry, boundary.geometry);" % (ways_table, sa_table, buffer)
clip_nodes = "DELETE FROM %s AS nodes USING %s AS boundary WHERE NOT ST_DWithin(nodes.geometry, boundary.geometry, %d) AND NOT ST_Intersects(nodes.geometry, boundary.geometry);" % (points_table, sa_table, buffer)

run_clip_w = run_query_pg(clip_ways, connection)
run_clip_n = run_query_pg(clip_nodes, connection)

#%%
#Check what clipped data looks like
ways = gpd.read_postgis(sql_ways, connection, geom_col='geometry')
ways.plot()
#%%
sql_file = open('classify_osm_waystable.sql','r')

classify_ways = run_query_pg(sql_file, connection, close=True)

#%%
#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
