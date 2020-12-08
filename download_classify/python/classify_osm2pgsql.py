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

'''
#OBS
cursor = connection.cursor()
try:
    cursor.execute(clear_rows_ways)
    print('Rows deleted from', ways_table)
    cursor.execute(clear_rows_rel)
    print('Rows deleted from', rel_table)
except(Exception, pg.Error) as error:
    print(error)

connection.commit()
'''
#%%
#Deleting unneccessary columns

#Columns to be dropped from ways table
ways_col = ['admin_level', 'amenity', 'area', 'boundary', 'harbour', 'horse', 'landuse', '"lanes:backward"', '"lanes:forward"', 'leisure', 'noexit', 'operator', 'railway', 'shop', 'traffic_sign', '"turn:lanes"', '"turn:backward"', '"turn:forward"', 'water', 'waterway', 'wetland', 'wood']
ways_del = ', DROP COLUMN '.join(ways_col)
ways_del = 'ALTER TABLE %s ' % ways_table + 'DROP COLUMN ' + ways_del + ';'
#%%
#Columns to be dropped from relations table
rel_useful_cols = ['osm_id', 'name', 'operator','ref','route','geometry']
rel_query = "SELECT * FROM %s" % rel_table
relations = gpd.read_postgis(rel_query, connection, geom_col='geometry')
rel_org_cols = list(relations.columns)
rel_cols_del = [i for i in rel_org_cols if i not in rel_useful_cols]
rel_del = '", DROP COLUMN "'.join(rel_cols_del)
rel_del = 'ALTER TABLE %s ' % rel_table + 'DROP COLUMN "' + rel_del + '";'

#%%
#Columns to be dropped from points table
points_useful_cols = ['osm_id','amenity','area','barrier','bicycle','bollard','crossing','crossing:island','crossing:ref','ele','flashing_lights','foot','highway','layer','lit','parking','public_transport','railway','ref','segregated','service:bicycle:chain_tool','service:bicycle:pump','service','shop','surface','traffic_calming','traffic_sign','traffic_signals','geometry']
points_query = "SELECT * FROM %s" % points_table
points = gpd.read_postgis(points_query, connection, geom_col='geometry')
points_org_cols = list(points.columns)
points_cols_del = [i for i in points_org_cols if i not in points_useful_cols]
points_del = '", DROP COLUMN "'.join(points_cols_del)
points_del = 'ALTER TABLE %s ' % points_table + 'DROP COLUMN "' + points_del + '";'

#%%
run_del_w = run_query_pg(ways_del, connection)
run_del_p = run_query_pg(points_del, connection)
run_del_r = run_query_pg(rel_del, connection)
'''
#OBS rewrite to function!
cursor = connection.cursor()
try:
    #cursor.execute(ways_del)
    print('Columns deleted from', ways_table)
    cursor.execute(points_del)
    print('Columns deleted from', points_table)
    #cursor.execute(rel_del)
    print('Columns deleted from', rel_table)
except(Exception, pg.Error) as error:
    print(error)

connection.commit()
'''

#%%

#Classifying ways table
ways_classi = open('sql/classify_osm_waystable.sql','r')

run_class_w = run_query_pg(ways_classi, connection)

'''
cursor = connection.cursor()

#OBS rewrite as function!
try:
    cursor.execute(ways_classi.read())
    print('Ways data reclassified')
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

connection.commit()
'''
#%%
#Classyfing points table
points_classi = open('sql/classify_osm_points.sql','r')

run_class_p = run_query_pg(points_classi, connection)

'''
cursor = connection.cursor()

#OBS! Rewrite to function!
try:
    cursor.execute(points_classi.read())
    print('Points data reclassified')
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

connection.commit()
'''
#%%
#Joining data about cycle routes to ways data
ways_relations = open('sql/join_relations_to_ways.sql','r')

run_ways_rel = run_query_pg(ways_relations, connection)

'''
cursor = connection.cursor()

#OBS rewrite as function!
try:
    cursor.execute(ways_relations.read())
    print('Relations data joined!')
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

connection.commit()
'''
#%%
# Testing the results

#Add here

#%%

#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
