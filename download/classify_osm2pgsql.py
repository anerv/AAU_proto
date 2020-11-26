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
clear_rows_ways = 'DELETE FROM %s WHERE highway IS NULL' % ways_table
#clear_rows_points = 'DELETE FROM %s WHERE XXX' % points_table
#clear_rows_rel = 'DELETE FROM %s WHERE XXX' % rel_table

#Deleting unneccessary columns
cursor = connection.cursor()
try:
    cursor.execute(clear_rows_ways)
    print('Rows deleted from', table_ways)
except(Exception, pg.Error) as error:
    print(error)

with engine.connect() as connection:
    try:
        result = connection.execute(clear_rows_ways)
        print('Rows deleted from', ways_table)
    except(Exception) as error:
        print('Problem deleting rows from', ways_table)
    try:
        result = connection.execute(copy_rel)
        print('Copy of table made for osm relations')
    except(Exception) as error:
        print('Problem copying table for osm relations')
    try:
        result = connection.execute(copy_points)
        print('Copy of table made for osm points')
    except(Exception) as error:
        print('Problem copying table for osm points')
    
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

#%%
connection.commit()

#%%
# Classifying relations table


#Classyfing points table

#%%
# Testing the results

#Add here

#%%

#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
