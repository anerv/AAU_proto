#%%
from config_download import *

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
def run_query_pg(query, connection,success='Query successful!',fail='Query failed!',commit=True,close=False):
    
    '''
    Function for running a sql query uding psycopg2
    Required input are query/filepath (string) to query and name of database connection
    Optional input are message to be printed when the query succeeds or fails, and whether the function should commit the changes (default is to commit)
    You must be connected to the database before using the function
    If query fails and returns error the function automatically reconnects to database
    '''
    cursor = connection.cursor()

    #Check whether query is a sql statement as string or a filepath to an sql file
    query_is_file = query.endswith('.sql')
    
    try:
        if query_is_file:
            open_query = open(query,'r')
            cursor.execute(open_query.read())
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        rows_changed = len(result)
        print(success)
        print(rows_changed,'rows were updated or retrieved')
    except(Exception) as error:
        print(fail)
        print(error)
        print('Reconnecting to the database. Please fix error before rerunning')
        connection.close()
        try:
            connection = pg.connect(database = database_name, user = db_user,
                                        password = db_password,
                                        host = db_host)

            print('You are connected to the database %s!' % database_name)

        except (Exception, pg.Error) as error :
            print("Error while connecting to PostgreSQL", error)

    if commit:
        connection.commit()
        print('Changes commited')
    else:
        print('Changes not commited')
    if close:
        connection.close()
        print('Connection closed')
    
    return result
#%%
#Testing
q1 = "SELECT * FROM wayskbh WHERE route_name ILIKE '%c%'"
q2 = 'test_sql.sql'

# %%
#test1 = run_query_pg(q1,connection, commit=False)
#%%
#test2 = run_query_pg(q1,connection, commit=False)

# %%
