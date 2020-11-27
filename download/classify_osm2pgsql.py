'''
This script runs several sql script and files to reclassify the osm data based on the original tags
Unused columns and rows are deleted (but can still be found in the table created from the original osm file)

TO DO

- slet unødvendige kolonner fra points
- klassificer rel
- klassificer points - hvilke vil jeg have?
'''
#%%
#Importing modules
import psycopg2 as pg
from config_download import *
import geopandas as gpd
# %%
# Connecting to the database
try:
    connection = pg.connect(database = database_name, user = db_user,
                                  password = db_password,
                                  host = db_host)

    print('You are connected to the database %s!' % database_name)

except (Exception, pg.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

#%%

#Delecting unneccessary rows
clear_rows_ways = "DELETE FROM %s WHERE highway IS NULL OR highway IN ('raceway', 'platform')" % ways_table
#clear_rows_points = 'DELETE FROM %s WHERE XXX' % points_table
clear_rows_rel = "DELETE FROM %s WHERE route NOT IN ('fitness_trail' , 'foot' , 'hiking' , 'bicycle', 'road' ) OR route IS NULL" % rel_table


cursor = connection.cursor()
try:
    cursor.execute(clear_rows_ways)
    print('Rows deleted from', ways_table)
    #cursor.execute(clear_rows_points)
    #print('Rows deleted from', points_table)
    cursor.execute(clear_rows_rel)
    print('Rows deleted from', rel_table)
except(Exception, pg.Error) as error:
    print(error)

connection.commit()
#%%
#Deleting unneccessary columns

#OBS rewrite to function!

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

#%%
connection.commit()
#%%

#Classifying ways table
sql_file = open('classify_osm_waystable.sql','r')
cursor = connection.cursor()

try:
    cursor.execute(sql_file.read())
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
#%%

# Classifying relations table


#Classyfing points table

connection.commit()

#%%
# Testing the results

#Add here

#%%

#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
