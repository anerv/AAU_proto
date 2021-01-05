'''
Configurations used in the analysis
'''

#Name of study area
area_name = '_rh'

#Filepath to polygon defining the study area
fp_sa = '../data/region_hovedstaden.gpkg'
sa_layer_name ="region_hovedstaden"

#Filepath to Corine land cover data
fp_lc = '../data/CLC12_DK.shp'
lc_layer_name = 'corine'

#Filepath to attribute data for Corine land cover
fp_att = '../data/clc_legend_modified.csv'

#Size of buffer in metres
buffer = 3000

# Define CRS
crs = 25832

# Database connection
db_user = 'postgres'
db_password = 'AAU20'
db_host = 'localhost'
db_name = 'rh'
db_port = '5432'

#Setting table names
ways_table = "ways" + area_name
points_table = "points" + area_name
rel_table = "rel" + area_name
sa_table = "study_area" + area_name
poly_table = "poly" + area_name
lu_table = "land_use" + area_name
