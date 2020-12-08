#%%
from config import *

#%%
#Function for connecting to database using psycopg2
def connect_pg(db_name, db_user, db_password, db_host='localhost'):
    '''
    Function for connecting to database using psycopg2
    Required input are database name, username, password
    If no host is provided localhost is assumed
    Returns the connection object
    '''
    import psycopg2 as pg

    # Connecting to the database
    try:
        connection = pg.connect(database = db_name, user = db_user,
                                  password = db_password,
                                  host = db_host)

        print('You are connected to the database %s!' % db_name)

        return connection

    except (Exception, pg.Error) as error :
        print ("Error while connecting to PostgreSQL", error)

    
#%%
#Testing
#connection = connect_pg(db_name, db_user, db_password)
#%%
#Function for running sql query using psycopg2
def run_query_pg(query,connection, success='Query successful!',fail='Query failed!',commit=True,close=False):
    
    '''
    Function for running a sql query using psycopg2
    Required input are query/filepath (string) to query and name of database connection
    Optional input are message to be printed when the query succeeds or fails, and whether the function should commit the changes (default is to commit)
    You must be connected to the database before using the function
    If query fails and returns error the function automatically reconnects to database
    '''
    import psycopg2 as pg

    cursor = connection.cursor()

    #Check whether query is a sql statement as string or a filepath to an sql file
    query_is_file = query.endswith('.sql')
    
    try:
        if query_is_file:
            open_query = open(query,'r')
            cursor.execute(open_query.read())
        else:
            cursor.execute(query)
        
        print(success)
        try:
            result = cursor.fetchall()
            rows_changed = len(result)
            print(rows_changed,'rows were updated or retrieved')
            return result

        except:
            pass

        if commit:
            connection.commit()
            print('Changes commited')
        else:
            print('Changes not commited')
        if close:
            connection.close()
            print('Connection closed')
    

    except(Exception) as error:
        print(fail)
        print(error)
        print('Reconnecting to the database. Please fix error before rerunning')
        connection.close()
        try:
            connection = pg.connect(database = db_name, user = db_user,
                                        password = db_password,
                                        host = db_host)

            print('You are connected to the database %s!' % db_name)

        except (Exception, pg.Error) as error :
            print("Error while connecting to PostgreSQL", error)

    
#%%
#Testing
q1 = "SELECT * FROM wayskbh WHERE route_name ILIKE '%c%'"
q2 = 'test_sql.sql'

# %%
#test1 = run_query_pg(q1,connection, commit=False)
#%%
#test2 = run_query_pg(q1,connection, commit=False)

# %%
#Function for connecting to database using sqlalchemy
def connect_alc(db_name, db_user, db_password, db_host='localhost'):
    '''
    Function for connecting to database using sqlalchemy
    Required input are database name, username, password
    If no host is provided localhost is assumed
    Returns the engine object
    '''
    import sqlalchemy

    #Create engine
    engine_info = 'postgresql://' + db_user +':'+ db_password + '@' + db_host + ':' + db_port + '/' + db_name

    #Connecting to database
    try:
        engine = sqlalchemy.create_engine(engine_info)
        engine.connect()
        print('You are connected to the database %s!' % db_name)
        return engine
    except(Exception, sqlalchemy.exc.OperationalError) as error:
        print('Error while connecting to the dabase!', error)

# %%
#engine_test = connect_alc(db_name, db_user, db_password)
# %%
#Function for loading data to database using sqlalchemy
def to_postgis(geodataframe, table_name, engine, if_exists='replace'):
    
    '''
    Function for loading a geodataframe to a postgres database using sqlalchemy
    Required input are geodataframe, desired name of table and sqlalchemy engine
    Default behaviour is to replace table if it already exists, but this can be changed to fail
    '''
    try:
        geodataframe.to_postgis(table_name, engine, if_exists=if_exists)
        print(table_name, 'successfully loaded to database!')
    except(Exception) as error:
        print('Error while uploading data to database:', error)

#%%
'''
import geopandas as gpd 
try:
    #if format is shapefile only path is needed
    study_area = gpd.read_file(fp_sa)
except(Exception) as error:
    #if format is geopackage use both filepath and layer name
    study_area = gpd.read_file(fp_sa, layer=layer_name)

testing_sa = to_postgis(study_area, 'sa_test', engine_test)
'''
# %%
# Function for running query using sqlalchemy
def run_query_alc(query, engine,success='Query successful!',fail='Query failed!'):
    with engine.connect() as connection:
        try:
            result = connection.execute(query)
            print(success)
            return result
        except(Exception) as error:
            print(fail)
            print(error)
#%%
#Testing
#q1 = "SELECT * FROM wayskbh WHERE route_name ILIKE '%%Amager%%'"
#test = run_query_alc(q1,engine_test)
# %%
