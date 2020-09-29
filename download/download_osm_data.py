'''
This scripts:
- downloads OSM data using the osmnx module
- converts the data to a geodataframe with nodes and edges
- uploads the data to a postgresql database
'''

#%%
#Importing modules!
import osmnx as ox
import geopandas as gp
import matplotlib.pyplot as plt
from config_download import crs
from sqlalchemy import create_engine
import psycopg2
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

# Plot study area for visual check
# OBS change title!!
study_area.plot()
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
'''
#%%
osm_nodes = gp.read_file(r"C:\Users\viero\OneDrive\Documents\AAU\AAU_Geodata\OSM_DATA.gpkg", layer='OSM_points')
node_tags1 = list(osm_nodes)
node_tags1.sort()
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
# Convert graph to pandas edgelist
gdf = ox.graph_to_gdfs(graph)
nodes= gdf[0]
edges = gdf[1]
# %%
