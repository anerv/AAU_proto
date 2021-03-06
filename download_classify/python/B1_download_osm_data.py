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
#import osmnx as ox
import geopandas as gp
import matplotlib.pyplot as plt
from config import *
import sqlalchemy
from database_functions import run_query_alc, connect_alc, to_postgis

#%%
# Provide polygon defining the study area
try:
    #if format is shapefile only path is needed
    study_area = gp.read_file(fp_sa)
except(Exception) as error:
    #if format is geopackage use both filepath and layer name
    study_area = gp.read_file(fp_sa, layer=layer_name)
    
#%%
# Check that study area crs is correct
osm_crs = "EPSG:4326"

if study_area.crs == osm_crs:
    print("The CRS for %s is okay" % area_name)
else:
    study_area = study_area.to_crs(osm_crs)
    print("Polygon for %s reprojected" % area_name)
#%%
# Plot study area for visual check
fig, ax = plt.subplots()
ax.set_title('Study area')
study_area.plot(ax=ax, facecolor='#ff3368')
#%%
#Creating bounding box for study area
bb = list(study_area.total_bounds)
#%%
#Unpacking list of bb values
west, south, east, north = bb
#%%
#Extract geometry from study area
#polygon = study_area.iloc[0]['geometry']
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
    "barrier",
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
#graph = ox.graph_from_polygon(polygon, network_type='all', simplify=False, retain_all=True, truncate_by_edge=True, clean_periphery=True, custom_filter=None)

graph = ox.graph_from_bbox(north, south, east, west, network_type='all', simplify=False, retain_all=True, truncate_by_edge=True, clean_periphery=True, custom_filter=None)
#%%
# Convert returned Multidigraph to undirected graph
graph = ox.get_undirected(graph)

#%%

# Plot graph
fig, ax = ox.plot_graph(graph, bgcolor='w', node_size= 0, edge_color='#ff3368', show=False, close=False)
ax.set_title('OSM network in %s' % area_name)
plt.show()
#%%
# Convert graph to pandas edgelist
gdf = ox.graph_to_gdfs(graph)
nodes = gdf[0]
edges = gdf[1]
# %%
#Connecting to db
engine = connect_alc(db_name, db_user, db_password)

#%%
# Uploading data to database
table_name_ways = 'osmways' + area_name
table_name_nodes = 'osmnodes' + area_name
table_name_sa = 'study_area' + area_name

ways_to_db = to_postgis(edges, table_name_ways, engine)
nodes_to_db = to_postgis(nodes, table_name_nodes, engine)
sa_to_db = to_postgis(study_area, table_name_sa, engine)

#%%
