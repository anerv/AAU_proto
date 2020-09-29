'''
This scripts downloads OSM data using the osmnx module
'''

#%%
#Importing modules!
import osmnx as ox
import geopandas as gp
import matplotlib.pyplot as plt
from config_download import crs
from sqlalchemy import create_engine
import psycopg2
import networkx as nx
#%%
# Provide polygon defining the study area
study_area = gp.read_file(r"C:\Users\viero\OneDrive\Documents\AAU\cph.gpkg", layer="Frb_boundary")

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

polygon = study_area.iloc[0]['geometry']
#%%
# Download OSM data as graph

#Define useful tags for nodes and ways
node_tags = ["access",
    "amenity",
    "bicycle",
    "bridge",
    "button_operated",
    "crossing",
    "flashing_lights",
    "foot",
    "highway",
    "junction",
    "leisure",
    "motorcar",
    "name",
    "oneway",
    "oneway:bicycle",
    "operator",
    "public_transport",
    "railway",
    "segregated",
    "shop",
    "stop",
    "surface",
    "traffic_sign",
    "traffic_signals",
    "tunnel",
    "width"]

way_tags = ["access",
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
    "flashing_lights",
    "foot",
    "footway",
    "highway",
    "junction",
    "landuse",
    "lanes",
    "lanes:forward",
    "lanes:backward",
    "lanes:both_ways",
    "leisure",
    "maxspeed",
    "motorcar",
    "name",
    "oneway",
    "oneway:bicycle",
    "operator",
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
    "shop",
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
    useful_tags_node=,
    useful_tags_way = [])

graph = ox.graph_from_polygon(polygon, network_type='all', simplify=True, retain_all=False, truncate_by_edge=False, clean_periphery=True, custom_filter=None)

#%%
# Convert returned Multidigraph to undirected graph
graph = ox.get_undirected(graph)
#%%
# Convert graph to pandas edgelist
gdf = ox.graph_to_gdfs(graph)
gdf2 = nx.to_pandas_edgelist(graph)
# %%
