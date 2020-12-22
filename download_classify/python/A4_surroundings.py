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
from pathlib import Path
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
att['CODE_12'] = att['CLC_CODE'].astype(int)
#%%
land_cover['CODE_12'] = land_cover['CODE_12'].astype(int)
#%%
# Join attribute data and spatial data
land_cover = land_cover.merge(att, on='CODE_12')
#%%
# Check that crs is correct
if land_cover.crs == crs:
    print("The CRS for land_cover is okay")
else:
    land_cover = land_cover.to_crs(crs)
    print("Data for land_cover reprojected")

#%%
#Change table names to lowercase
land_cover.columns = land_cover.columns.str.lower()
#%%
# Load to db
to_postgis(land_cover, 'land_cover', engine)

# Add spatial index
index_lc = "CREATE INDEX lc_geom_idx ON land_cover USING GIST (geometry);"
create_index = run_query_alc(index_lc, engine)
#%%
#Create new table with land cover cut to study area
lc_sa = "CREATE TABLE lc_sa AS (SELECT objectid, label_modified, code_12, label1, label2, label3, lc.geometry FROM land_cover lc, study_area_rh sa WHERE ST_Intersects(lc.geometry, sa.geometry));"
run_lc_sa = run_query_alc(lc_sa, engine)
run_sa_ind = run_query_alc("CREATE INDEX lc_sa_geom_idx ON lc_sa USING GIST (geometry);",engine)

#Remove polygon with ocean
#Must be adapted if the use of objectid in Danish corine data changes
remove_oc = run_query_alc("DELETE FROM lc_sa WHERE objectid = 1;",engine)

#%%
#Creating table with coastlines
cl = '''CREATE TABLE coastline AS (SELECT * FROM planet_osm_line WHERE "natural" = 'coastline');'''
run_cl = run_query_alc(cl, engine)
#%%
#Rename geometry column
rename_c = run_query_alc("ALTER TABLE coastline RENAME COLUMN way TO geometry", engine)

#Reproject
reproj = "ALTER TABLE coastline ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (crs, crs)
reproject_ways = run_query_alc(reproj, engine)

# Create spatial index for coastlines
index_cl = "CREATE INDEX cl_geom_idx ON coastline USING GIST (geometry);"
run_index = run_query_alc(index_cl, engine)
# %%
# Update attribute for ways based on land cover
#run file
two_levels_up = str(Path(__file__).parents[1])
fp = two_levels_up + '\\sql\\land_cover.sql'

connection = connect_pg(db_name, db_user, db_password, db_host)
run_lc = run_query_pg(fp, connection)

# %%
