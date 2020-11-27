'''
This script runs several sql files to reclassify the osm data based on the original tags
TO DO

- slet unødvendige kolonner fra ways, relations, points
- klassificer ways
- klassificer rel
- klassificer points - hvilke vil jeg have?
'''
#%%
#Importing modules
import psycopg2 as pg
from config_download import *
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
#clear_rows_rel = 'DELETE FROM %s WHERE XXX' % rel_table


cursor = connection.cursor()
try:
    cursor.execute(clear_rows_ways)
    print('Rows deleted from', ways_table)
    #cursor.execute(clear_rows_points)
    #print('Rows deleted from', points_table)
    #cursor.execute(clear_rows_rel)
    #print('Rows deleted from', rel_table)
except(Exception, pg.Error) as error:
    print(error)

#%%
#Deleting unneccessary columns

#Columns to be dropped from ways table
col_ways = ['admin_level', 'amenity', 'area', 'boundary', 'harbour', 'horse', 'landuse', '"lanes:backward"', '"lanes:forward"', 'leisure', 'noexit', 'operator', 'railway', 'shop', 'traffic_sign', '"turn:lanes"', '"turn:backward"', '"turn:forward"', 'water', 'waterway', 'wetland', 'wood']
del_ways = ', DROP COLUMN '.join(col_ways)
del_ways = 'ALTER TABLE %s ' % ways_table + 'DROP COLUMN ' + del_ways + ';'
#%%

#Columns to be dropped from rel table
#Columns to be dropped from points table

cursor = connection.cursor()
try:
    cursor.execute(del_ways)
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
