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
# Testing the results

#Add here
#%%
# Classifying relations table


#Classyfing points table

#Delecting unneccessary rows

#Deleting unneccessary columns


#Commiting changes and closing db connection
connection.commit()
connection.close()
# %%
