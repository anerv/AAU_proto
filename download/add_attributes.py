'''
This script adds additional attributes to ways table.
The data added here are information about street lights and traffic counts but can be replaced with other point data
'''
#%%
#Importing modules
import psycopg2 as pg
from config_download import *
from database_functions import connect_pg, run_query_pg
# %%
#File paths to data
light =
traffic = 