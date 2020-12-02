'''
This script prepares the original osm data downloaded using osm2pgsql
'''
#%%
#Importing modules
from config_download import *
import geopandas as gpd
import sqlalchemy

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
engine_info = 'postgresql://' + db_user +':'+ db_password + '@' + db_host + ':' + db_port + '/' + database_name

#Connecting to database
try:
    engine = sqlalchemy.create_engine(engine_info)
    engine.connect()
    print('You are connected to the database %s!' % database_name)
except(Exception, sqlalchemy.exc.OperationalError) as error:
    print('Error while connecting to the dabase!', error)

#%%
#Loading study area to database
table_name_sa = 'study_area' + area_name
try:
    study_area.to_postgis(table_name_sa, engine, if_exists='replace')
    print('Study area successfully loaded to database!')
except(Exception) as error:
    print('Error while uploading study area data to database:', error)

#%%
#Checking table names
print('Table names are:', ways_table, points_table, rel_table, sa_table)

#%%
# Creating new tables
copy_ways = "CREATE TABLE %s AS SELECT * FROM planet_osm_line WHERE osm_id > 0;" % ways_table
copy_points = "CREATE TABLE %s AS TABLE planet_osm_point;" % points_table
copy_rel = "CREATE TABLE %s AS SELECT * FROM planet_osm_line WHERE osm_id < 0;" % rel_table

#OBS rewrite to function!
with engine.connect() as connection:
    try:
        result = connection.execute(copy_ways)
        print('Copy of table made for osm ways')
    except(Exception) as error:
        print('Problem copying table for osm ways')
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
#Renaming geomtry columns
#Using osm2pgsql the geometry col is initially called 'way'
rename1 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % ways_table
rename2 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % points_table
rename3 = 'ALTER TABLE %s RENAME COLUMN way TO geometry;' % rel_table

#OBS rewrite to function!
with engine.connect() as connection:
    try:
        result = connection.execute(rename1)
        print('Column in ways table renamed')
    except(Exception) as error:
        print('Problem renaming column in ways table')
        print(error)
    try:
        result = connection.execute(rename2)
        print('Column in points table renamed')
    except(Exception) as error:
        print('Problem renaming column in points table')
        print(error)
    try:
        result = connection.execute(rename3)
        print('Column in ways table renamed')
    except(Exception) as error:
        print('Problem renaming column in relations table')
        print(error)
   
#%%
#Reprojecting data
reproj1 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (ways_table, crs, crs)

reproj2 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(POINT,%d) USING ST_Transform(geometry,%d)" % (points_table, crs, crs)

reproj3 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(LINESTRING,%d) USING ST_Transform(geometry,%d)" % (rel_table, crs, crs)

reproj4 = "ALTER TABLE %s ALTER COLUMN geometry TYPE geometry(MULTIPOLYGON,%d) USING ST_Transform(geometry,%d)" % (sa_table, crs, crs)

#OBS rewrite to function!
with engine.connect() as connection:
    try:
        result = connection.execute(reproj1)
        print('Ways table reprojected')
    except(Exception) as error:
        print('Problem reprojecting ways table')
        print(error)
    try:
        result = connection.execute(reproj2)
        print('Points table reprojected')
    except(Exception) as error:
        print('Problem reprojecting points table')
        print(error)
    try:
        result = connection.execute(reproj3)
        print('Relations table reprojected')
    except(Exception) as error:
        print('Problem reprojecting relations table')
        print(error)
    try:
        #results = connection.execute(reproj4)
        print('Study area reprojected')
    except(Exception) as error:
        print('Problem reprojecting study area table')
        print(error)

#%%
#Check projections
ways_crs = "SELECT find_SRID('public', '%s', 'geometry');" % ways_table
points_crs = "SELECT find_SRID('public', '%s', 'geometry');" % points_table
rel_crs = "SELECT find_SRID('public', '%s', 'geometry');" % rel_table
sa_crs = "SELECT find_SRID('public', '%s', 'geometry');" % sa_table

with engine.connect() as connection:
    check_ways = list(connection.execute(ways_crs))[0][0]
    check_points = list(connection.execute(points_crs))[0][0]
    check_rel = list(connection.execute(rel_crs))[0][0]
    check_sa = list(connection.execute(sa_crs))[0][0]

if check_ways == check_points == check_rel == check_sa:
    print('All data are in the same projection!')
else:
    print('All tables are not in the same projection!')
#%%
#Create spatial indexes
index_ways = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (ways_table,ways_table)
index_rel = "CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (rel_table,rel_table)
index_points ="CREATE INDEX %s_geom_idx ON %s USING GIST (geometry);" % (points_table,points_table)

#OBS rewrite to function!
with engine.connect() as connection:
    try:
        result = connection.execute(index_ways)
        print('Index created')
    except(Exception) as error:
        print('Problem creating spatial index')
        print(error)
    try:
        result = connection.execute(index_rel)
        print('Index created')
    except(Exception) as error:
        print('Problem creating spatial index')
        print(error)
    try:
        result = connection.execute(index_points)
        print('Index created')
    except(Exception) as error:
        print('Problem creating spatial index')
        print(error)
 
#%%
#Option to clip data to study area
#Uncomment if data should be clipped to the extent of the study area + buffer

#OBS rewrite to function!
'''
clip_ways = "DELETE FROM %s AS ways USING %s AS boundary WHERE NOT ST_DWithin(ways.geometry, boundary.geometry, %d) AND NOT ST_Intersects(ways.geometry, boundary.geometry);" % (ways_table, sa_table, buffer)
clip_points = "DELETE FROM %s AS points USING %s AS boundary WHERE NOT ST_DWithin(points.geometry, boundary.geometry, %d) AND NOT ST_Intersects(points.geometry, boundary.geometry);" % (points_table, sa_table, buffer)
clip_rels =  "DELETE FROM %s AS rel USING %s AS boundary WHERE NOT ST_DWithin(rel.geometry, boundary.geometry, %d) AND NOT ST_Intersects(rel.geometry, boundary.geometry);" % (points_table, sa_table, buffer)

with engine.connect() as connection:
    try:
        connection.execute(clip_ways)
        print('The ways dataset have been clipped!')
        connection.execute(clip_points)
        print('The point dataset have been clipped!')
        connection.execute(clip_rels)
        print('The relations dataset have been clipped!')
    except(Exception) as error:
        print(error)
'''

#%%
