'''
This script prepares the original osm data downloaded using osm2pgsql
'''
#%%
#Importing modules
from config import *
from database_functions import connect_alc, to_postgis, run_query_alc
import geopandas as gpd
import sqlalchemy
import psycopg2 as pg
#%%
# Creating engine to connect to database
engine = connect_alc(db_name, db_user, db_password)
#%%
# Provide polygon defining the study area
try:
    #if format is shapefile only path is needed
    study_area = gpd.read_file(fp_sa)
except(Exception) as error:
    #if format is geopackage use both filepath and layer name
    study_area = gpd.read_file(fp_sa, layer=sa_layer_name)

#study_area.plot()

#%%
#Loading study area to database
table_name_sa = 'study_area_' + area_name
to_postgis(study_area, table_name_sa, engine)

#%%
'''
# Polygons defining administrative boundaries, if different from study area
#Uncomment if adm layer is needed
try:
    #if format is shapefile only path is needed
    adm_boundary = gpd.read_file(fp_adm)
except(Exception) as error:
    #if format is geopackage use both filepath and layer name
    adm_boundary = gpd.read_file(fp_adm, layer=adm_layer_name)

#Loading adm boundary to database
table_name_adm = 'adm_bound_' + area_name
to_postgis(adm_boundary, table_name_adm, engine)
'''
#%%
#Checking table names
print('Table names are:', ways_table, points_table, rel_table, sa_table, lu_table, adm_table)

#%%
# Creating new tables
copy_ways = "CREATE TABLE %s AS SELECT * FROM planet_osm_line WHERE osm_id > 0;" % ways_table
copy_points = "CREATE TABLE %s AS TABLE planet_osm_point;" % points_table
#Create table with relations data
copy_rel = "CREATE TABLE %s AS SELECT * FROM planet_osm_line WHERE osm_id < 0;" % rel_table
#Create table with land use data
copy_lu = 'CREATE TABLE %s AS (SELECT osm_id, amenity, landuse, leisure, water, "natural", man_made, way FROM planet_osm_polygon WHERE amenity IS NOT NULL OR landuse IS NOT NULL OR leisure IS NOT NULL OR "natural" IS NOT NULL OR water IS NOT NULL);' % lu_table

create_ways = run_query_alc(copy_ways, engine, success='Copy of table made for ways')
create_points = run_query_alc(copy_points, engine, success='Copy of table made for points')
create_relations = run_query_alc(copy_rel, engine, success='Copy of table made for relations')
create_lu = run_query_alc(copy_lu, engine, success='Copy of table made for land use')
#%%
#Renaming geomtry columns
#Using osm2pgsql the geom col is initially called 'way'
rename1 = 'ALTER TABLE %s RENAME COLUMN way TO geom;' % ways_table
rename2 = 'ALTER TABLE %s RENAME COLUMN way TO geom;' % points_table
rename3 = 'ALTER TABLE %s RENAME COLUMN way TO geom;' % rel_table
rename4 = 'ALTER TABLE %s RENAME COLUMN way TO geom;' % lu_table

rename_ways = run_query_alc(rename1, engine)
rename_points = run_query_alc(rename2, engine)
rename_rels = run_query_alc(rename3, engine)
rename_lu = run_query_alc(rename4, engine)

#%%
#Reprojecting data
reproj1 = "ALTER TABLE %s ALTER COLUMN geom TYPE geom(LINESTRING,%d) USING ST_Transform(geom,%d)" % (ways_table, crs, crs)

reproj2 = "ALTER TABLE %s ALTER COLUMN geom TYPE geom(POINT,%d) USING ST_Transform(geom,%d)" % (points_table, crs, crs)

reproj3 = "ALTER TABLE %s ALTER COLUMN geom TYPE geom(LINESTRING,%d) USING ST_Transform(geom,%d)" % (rel_table, crs, crs)

reproj4 = "ALTER TABLE %s ALTER COLUMN geom TYPE geom(MULTIPOLYGON,%d) USING ST_Transform(geom,%d)" % (sa_table, crs, crs)

reproj5 = "ALTER TABLE %s ALTER COLUMN geom TYPE geom(POLYGON,%d) USING ST_Transform(geom,%d)" % (lu_table, crs, crs)

reproject_ways = run_query_alc(reproj1, engine)
reproject_points = run_query_alc(reproj2, engine)
reproject_relations = run_query_alc(reproj3, engine)
reproject_sa = run_query_alc(reproj4, engine)
reproject_lu = run_query_alc(reproj5, engine)

#%%
#Check projections
ways_crs = "SELECT find_SRID('public', '%s', 'geom');" % ways_table
points_crs = "SELECT find_SRID('public', '%s', 'geom');" % points_table
rel_crs = "SELECT find_SRID('public', '%s', 'geom');" % rel_table
sa_crs = "SELECT find_SRID('public', '%s', 'geom');" % sa_table
lu_crs = "SELECT find_SRID('public', '%s', 'geom');" % lu_table

with engine.connect() as connection:
    check_ways = list(connection.execute(ways_crs))[0][0]
    check_points = list(connection.execute(points_crs))[0][0]
    check_rel = list(connection.execute(rel_crs))[0][0]
    check_sa = list(connection.execute(sa_crs))[0][0]
    check_lu = list(connection.execute(lu_crs))[0][0]

if check_ways == check_points == check_rel == check_sa:
    print('All data are in the same projection!')
else:
    print('All tables are not in the same projection!')
#%%
#Create spatial indexes
index_ways = "CREATE INDEX %s_geom_idx ON %s USING GIST (geom);" % (ways_table,ways_table)
index_rel = "CREATE INDEX %s_geom_idx ON %s USING GIST (geom);" % (rel_table,rel_table)
index_points = "CREATE INDEX %s_geom_idx ON %s USING GIST (geom);" % (points_table,points_table)
index_sa = "CREATE INDEX %s_geom_idx ON %s USING GIST (geom);" % (sa_table,sa_table)
index_lu = "CREATE INDEX %s_geom_idx ON %s USING GIST (geom);" % (lu_table,lu_table)

create_index_w = run_query_alc(index_ways, engine)
create_index_p = run_query_alc(index_rel, engine)
create_index_rel = run_query_alc(index_points, engine)
create_index_sa = run_query_alc(index_sa, engine)
create_index_lu = run_query_alc(index_lu, engine)

#%%
#Option to clip data to study area
#Uncomment if data should be clipped to the extent of the study area + buffer

'''
clip_ways = "DELETE FROM %s AS ways USING %s AS boundary WHERE NOT ST_DWithin(ways.geom, boundary.geom, %d) AND NOT ST_Intersects(ways.geom, boundary.geom);" % (ways_table, sa_table, buffer)
clip_points = "DELETE FROM %s AS points USING %s AS boundary WHERE NOT ST_DWithin(points.geom, boundary.geom, %d) AND NOT ST_Intersects(points.geom, boundary.geom);" % (points_table, sa_table, buffer)
clip_rels =  "DELETE FROM %s AS rel USING %s AS boundary WHERE NOT ST_DWithin(rel.geom, boundary.geom, %d) AND NOT ST_Intersects(rel.geom, boundary.geom);" % (points_table, sa_table, buffer)

run_clip_w = run_query_alc(clip_ways2, engine)
run_clip_p = run_query_alc(clip_points, engine)
run_clip_r = run_query_alc(clip_rels, engine)
'''

# %%
#The clipping method above can be very slow if the osm file covers a large area
#Alternatively use a GIS and load clipped data to database

#Filepaths to clipped files
ways_fp = r'C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\ways_clipped.gpkg'
rel_fp = r'C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\rel_clipped.gpkg'
points_fp =  r'C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\points_clipped.gpkg'
lu_fp = r'C:\Users\OA03FG\Aalborg Universitet\Urban Research group - General\AAU data\AAU grunddata\PROTOTYPE\lu_clipped.gpkg'

#%%
#Load clipped data to geodataframes
ways_clipped = gpd.read_file(ways_fp, layer='ways_clipped')
#%%
rel_clipped = gpd.read_file(rel_fp, layer='rel_clipped')
points_clipped = gpd.read_file(points_fp, layer='points_clipped')
lu_clipped = gpd.read_file(lu_fp, layer='lu_clipped')

# %%
#Load data to db
to_postgis(ways_clipped,'ways_clipped',engine)
to_postgis(rel_clipped,'rel_clipped',engine)
to_postgis(points_clipped,'points_clipped',engine)
to_postgis(lu_clipped,'lu_clipped',engine)
# %%
