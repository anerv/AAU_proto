'''
This scripts:
- downloads OSM data using the osmnx module
- converts the data to a geodataframe with nodes and edges
- uploads the data to a postgresql database
- a postgresql database must be created beforehand
- the database should have the postgis extension enabled
'''

#%%
#Importing modules!
import osmnx as ox
import geopandas as gp
import shapely
import matplotlib.pyplot as plt
from config_download import crs, db_user, db_password, db_host, database_name, db_port
import sqlalchemy
from geoalchemy2 import Geometry, WKTElement
import psycopg2 as pg
#%%
# Provide polygon defining the study area
study_area = gp.read_file(r"C:\Users\viero\OneDrive\Documents\AAU\AAU_Geodata\cph.gpkg", layer="Frb_boundary")

osm_crs = "EPSG:4326"
# Check that study area crs is correct
if study_area.crs == osm_crs:
    print("The CRS for study area is okay")
else:
    study_area = study_area.to_crs(osm_crs)
    print("Study area reprojected")
#%%
# Plot study area for visual check
fig, ax = plt.subplots()
ax.set_title('Study area')
study_area.plot(ax=ax, facecolor='#ff3368')
#%%
#Extract geometry from study area
polygon = study_area.iloc[0]['geometry']
#%%
#OBS remove later
'''
# Getting tages from OSM data
osm_ways = gp.read_file(r"C:\Users\viero\OneDrive\Documents\AAU\AAU_Geodata\OSM_DATA.gpkg", layer='OSM_ways')
way_tags1 = list(osm_ways)
way_tags1.sort()

osm_nodes = gp.read_file(r"C:\Users\viero\OneDrive\Documents\AAU\AAU_Geodata\OSM_DATA.gpkg", layer='OSM_points')
node_tags1 = list(osm_nodes)
node_tags1.sort()

'''
#%%
#Define useful tags for nodes and ways in OSM
node_tags = [
    "access",
    "amenity",
    "barrier",
    "bicycle",
    "bollard",
    "bridge",
    "bus",
    "button_operated",
    "crossing",
    "crossing:island",
    "flashing_lights",
    "foot",
    "highway",
    "junction",
    "leisure",
    "mapillary,"
    "motor_vehicle",
    "motorcar",
    "name",
    "noexit",
    "oneway",
    "oneway:bicycle",
    "operator",
    "osm_id",
    "parking",
    "public_transport",
    "railway",
    "segregated",
    "service:bicycle:chain_tool",
    "service:bicycle:pump",
    "shop",
    "stop",
    "subway",
    "surface",
    "traffic_calming",
    "traffic_sign",
    "traffic_signals",
    "tunnel",
    "width"]

way_tags = [
    "access",
    "barrier"
    "bridge",
    "bicycle",
    "button_operated",
    "crossing",
    "cycleway",
    "cycleway:left",
    "cycleway:right",
    "cycleway:both",
    "cycleway:buffer",
    "cycleway:left:buffer",
    "cycleway:right:buffer",
    "cycleway:both:buffer",
    "cycleway:width",
    "cycleway:left:width",
    "cycleway:right:width",
    "cycleway:both:width",
    "cycle_way:surface",
    "flashing_lights",
    "foot",
    "footway",
    "highway",
    "inclince",
    "junction",
    "landuse",
    "lanes",
    "lanes:forward",
    "lanes:backward",
    "lanes:both_ways",
    "layer",
    "leisure",
    "level",
    "lit",
    "mapillary,"
    "maxspeed",
    "maxspeed:advisory",
    "moped",
    "moter_vehicle",
    "motorcar",
    "name",
    "name:etymology:wikidata",
    "oneway",
    "oneway:bicycle",
    "operator",
    "osm_id",
    "parking",
    "parking:lane",
    "parking:lane:right",
    "parking:lane:left",
    "parking:lane:both",
    "parking:lane:width",
    "parking:lane:right:width",
    "parking:lane:left:width",
    "parking:lane:both:width",
    "public_transport",
    "railway",
    "segregated",
    "service",
    "sidewalk",
    "shop",
    "source_maxspeed",
    "stop",
    "surface",
    "tracktype",
    "traffic_sign",
    "traffic_signals:direction",
    "tunnel",
    "turn:lanes",
    "turn:lanes:both_ways",
    "turn:lanes:backward",
    "turn:lanes:forward",
    "width",
    "width:lanes",
    "width:lanes:forward",
    "width:lanes:backward"]

ox.utils.config(use_cache=True, 
    useful_tags_node= node_tags,
    useful_tags_way = way_tags)

#%%
# Download OSM data as graph

graph = ox.graph_from_polygon(polygon, network_type='all', simplify=True, retain_all=False, truncate_by_edge=False, clean_periphery=True, custom_filter=None)

#%%
# Convert returned Multidigraph to undirected graph
graph = ox.get_undirected(graph)
#%%
# Plot graph
fig, ax = ox.plot_graph(graph, bgcolor='w', node_size= 0, edge_color='#ff3368', show=False, close=False)
ax.set_title('OSM network in study area')
plt.show()
#%%
# Convert graph to pandas edgelist
gdf = ox.graph_to_gdfs(graph)
nodes= gdf[0]
edges = gdf[1]
# %%
# Creating engine to connect to database
engine_info = 'postgresql://' + db_user +':'+ db_password + '@' + db_host + ':' + db_port + '/' + database_name

#Connecting to database
try:
    engine = sqlalchemy.create_engine(engine_info)
    engine.connect()
    print('You are connected to the database!')
except(Exception, sqlalchemy.exc.OperationalError) as error:
    print('Error while connecting to the dabase!', error)

#%%
test = edges[['osmid', 'cycleway', 'geometry']]
test.to_postgis('test',engine)

#%%
table_name_ways = 'ways'

edges.to_postgis(table_name_ways, engine, if_exists='replace')


#%%
# Processing dataframes before loading to database
edges['geom'] = edges['geometry'].apply(lambda x: WKTElement(x.wkt, srid=osm_crs))
#edges.set_geometry('geom')
#%%
#drop the geometry column as it is now duplicative
edges.drop('geometry', 1, inplace=True)

#Set geom as geometry column

#%%
# For the geom column, we will use GeoAlchemy's type 'Geometry'

edges.to_sql('OSM_ways', engine, if_exists='replace', dtype={'geom':Geometry(geometry_type ="LINESTRING", srid=4326)})
#edges.to_sql('OSM_ways', engine, if_exists='replace')

#%%
# Creating the table for edges/ways and loading it into the database
edges.to_sql('OSM_edges', engine, if_exists='replace')

#%%

#Connecting to database
try:
    connection = pg.connect(database = database_name, user = db_user,
                                  password = db_password,
                                  host = db_host)

    cursor = connection.cursor()

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to the database","\n")

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

#%%
'''
need both table for nodes edges and boundary?