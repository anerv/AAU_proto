'''
This script runs several sql script and files to reclassify the osm data based on the original tags

TO DO

- slet unødvendige kolonner fra relations, points
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
clear_rows_rel = "DELETE FROM %s WHERE route NOT IN ('fitness_trail' , 'foot' , 'hiking' , 'bicycle', 'road' )" % rel_table


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

#Columns to be dropped from ways table
ways_col = ['admin_level', 'amenity', 'area', 'boundary', 'harbour', 'horse', 'landuse', '"lanes:backward"', '"lanes:forward"', 'leisure', 'noexit', 'operator', 'railway', 'shop', 'traffic_sign', '"turn:lanes"', '"turn:backward"', '"turn:forward"', 'water', 'waterway', 'wetland', 'wood']
ways_del = ', DROP COLUMN '.join(col_ways)
ways_del = 'ALTER TABLE %s ' % ways_table + 'DROP COLUMN ' + del_ways + ';'

#Columns to be dropped from relations table

#%%
rel_useful_cols = ['osmid','operator','ref','route',]
rel_query = "SELECT * FROM %s" % rel_table
relations = gpd.read_postgis(rel_query, connection, geom_col='geometry')
rel_org_cols = list(relations.columns)
rel_cols_del = [i for i in rel_org_cols if i not in rel_useful_cols]
#%%

#Columns to be dropped from points table

cursor = connection.cursor()
try:
    cursor.execute(ways_del)
    print('Columns deleted from', ways_table)
    #cursor.execute(clear_rows_points)
    #print('Rows deleted from', points_table)
    #cursor.execute(clear_rows_rel)
    #print('Rows deleted from', rel_table)
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
