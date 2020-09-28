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
ox.config(use_cache=True, 
    useful_tags_node=[],
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
