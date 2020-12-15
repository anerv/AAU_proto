'''
This script uses data about the land use to determine the surroudings of the infrastructure
'''
#%%
#Importing modules
from config import *
from database_functions import run_query_pg, run_query_alc, to_postgis, connect_pg, connect_alc
import sqlalchemy
import psycopg2
# %%
connection = connect_pg(db_name, db_user, db_password)
#%%

# %%


