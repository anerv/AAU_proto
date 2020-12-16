'''
This script uses data about the land use to determine the surroudings of the infrastructure
The data for land cover is a Corine land cover dataset (can be downloaded from e.g. Kortforsyningen)
The Corina data for Denmark tend to classify water near a harbour as harbour area. 
Therefore the coastline data from OSM is used as a supplement to determine whether an element is close to water/coast
'''
#%%
#Importing modules
from config import *
from database_functions import run_query_pg, run_query_alc, to_postgis, connect_pg, connect_alc
import sqlalchemy
import psycopg2
import geopandas as gpd
import pandas as pd
# %%
# Connection to db
#connection = connect_pg(db_name, db_user, db_password)
engine = connect_alc(db_name, db_user, db_password)
#%%
# Read data with land cover
try:
    #if format is shapefile only path is needed
    land_cover = gpd.read_file(fp_lc)
except(Exception) as error:
    #if format is geopackage use both filepath and layer name
    land_cover = gpd.read_file(fp_lc, layer=lc_layer_name)
#%%
# Read data with the attribute info for land cover data
att = pd.read_csv(fp_att, sep=';')
#%%
#Remove empty rows
att.dropna(how='all')

# Rename column to join columns have the same name, convert float to integer
att['CODE_06'] = att['CLC_CODE'].astype(int)
#%%
land_cover['CODE_06'] = land_cover['CODE_06'].astype(int)
#%%
# Join attribute data and spatial data
land_cover = land_cover.merge(att, on='CODE_06')
#%%
# Check that crs is correct
if land_cover.crs == crs:
    print("The CRS for land_cover is okay")
else:
    land_cover = land_cover.to_crs(crs)
    print("Data for land_cover reprojected")

#%%
# Load to db
to_postgis(land_cover, 'land_cover', engine)

#%%
# Add spatial index
index_lc = "CREATE INDEX lc_geom_idx ON land_cover USING GIST (geometry);"

create_index = run_query_alc(index_lc, engine)
#%%
# Simplify - dissolving adjacent polygons with identical attributes
# %%
postgis_cookbook=# CREATE TABLE chp03.states_from_counties ASSELECT ST_Multi(ST_Union(the_geom)) as the_geom, state_fips FROM chp03.countiesGROUP BY state_fips;


