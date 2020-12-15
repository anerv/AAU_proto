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
# Provide polygon defining the study area
try:
    #if format is shapefile only path is needed
    study_area = gpd.read_file(fp_sa)
except(Exception) as error:
    #if format is geopackage use both filepath and layer name
    study_area = gpd.read_file(fp_sa, layer=layer_name)

#study_area.plot()

#%%
# Creating engine to connect to database
engine = connect_alc(db_name, db_user, db_password)

#%%
#Loading study area to database
table_name_sa = 'study_area' + area_name
upload_sa = to_postgis(study_area, table_name_sa, engine)

#%%
#Checking table names
print('Table names are:', ways_table, points_table, rel_table, sa_table)

#%%
# Creating new tables
copy_ways = "CREATE TABLE %s AS SELECT * FROM planet_osm_line WHERE osm_id > 0;" % ways_table
copy_points = "CREATE TABLE %s AS TABLE planet_osm_point;" % points_table
#Create table with relations data
copy_rel = "CREATE TABLE %s AS SELECT * FROM planet_osm_line WHERE osm_id < 0;" % rel_table
#Create table with land use data
copy_lu = "CREATE TABLE %s AS (SELECT osm_id, amenity, landuse, leisure, water, natural, way FROM planet_osm_polygon WHERE amenity IS NOT NULL OR landuse IS NOT NULL OR leisure IS NOT NULL);" % lu_table

create_ways = run_query_alc(copy_ways, engine, success='Copy of table made for osm ways')
create_points = run_query_alc(copy_points, engine, success='Copy of table made for osm points')
create_relations = run_query_alc(copy_rel, engine, success='Copy of table made for osm relations')
create_lu = run_query_alc(copy_lu, engine, success='Copy of table made for osm relations')
#%%
#Renaming geomtry columns
#Using osm2pgsql the geometry col is initially called 'way'
rename1 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % ways_table
rename2 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % points_table
rename3 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % rel_table
rename4 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % lu_table

rename_ways = run_query_alc(rename1, engine)
rename_points = run_query_alc(rename2, engine)
rename_rels = run_query_alc(rename3, engine)
rename_lu = run_query_alc(rename4, engine)

#%%
#Reprojecting data
reproj1 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (ways_table, crs, crs)

reproj2 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(POINT,%d) USING ST_Transform(geometry,%d)" % (points_table, crs, crs)

reproj3 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (rel_table, crs, crs)

reproj4 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(MULTIPOLYGON,%d) USING ST_Transform(geometry,%d)" % (sa_table, crs, crs)

reproj5 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(POLYGON,%d) USING ST_Transform(geometry,%d)" % (lu_table, crs, crs)

reproject_ways = run_query_alc(reproj1, engine)
reproject_points = run_query_alc(reproj2, engine)
reproject_relations = run_query_alc(reproj3, engine)
reproject_sa = run_query_alc(reproj4, engine)
reproject_lu = run_query_alc(reproj5, engine)

#%%
#Check projections
ways_crs = "SELECT find_SRID('public', '%s', 'geometry');" % ways_table
points_crs = "SELECT find_SRID('public', '%s', 'geometry');" % points_table
rel_crs = "SELECT find_SRID('public', '%s', 'geometry');" % rel_table
sa_crs = "SELECT find_SRID('public', '%s', 'geometry');" % sa_table
lu_crs = "SELECT find_SRID('public', '%s', 'geometry');" % lu_table

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
index_ways = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (ways_table,ways_table)
index_rel = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (rel_table,rel_table)
index_points = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (points_table,points_table)
index_sa = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (sa_table,sa_table)
index_lu = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (lu_table,lu_table)

create_index_w = run_query_alc(index_ways, engine)
create_index_p = run_query_alc(index_rel, engine)
create_index_rel = run_query_alc(index_points, engine)
create_index_sa = run_query_alc(index_sa, engine)
create_index_lu = run_query_alc(index_lu, engine)

#%%
#Option to clip data to study area
#Uncomment if data should be clipped to the extent of the study area + buffer
'''
clip_ways = "DELETE FROM %s AS ways USING %s AS boundary WHERE NOT ST_DWithin(ways.geometry, boundary.geometry, %d) AND NOT ST_Intersects(ways.geometry, boundary.geometry);" % (ways_table, sa_table, buffer)
clip_points = "DELETE FROM %s AS points USING %s AS boundary WHERE NOT ST_DWithin(points.geometry, boundary.geometry, %d) AND NOT ST_Intersects(points.geometry, boundary.geometry);" % (points_table, sa_table, buffer)
clip_rels =  "DELETE FROM %s AS rel USING %s AS boundary WHERE NOT ST_DWithin(rel.geometry, boundary.geometry, %d) AND NOT ST_Intersects(rel.geometry, boundary.geometry);" % (points_table, sa_table, buffer)

run_clip_w = run_query_alc(clip_ways, engine)
run_clip_p = run_query_alc(clip_points, engine)
run_clip_r = run_query_alc(clip_rels, engine)
'''
#%%
