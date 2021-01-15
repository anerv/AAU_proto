'''
Configurations used in the analysis
'''

#Name of study area
area_name = 'rh'

#Filepath to polygon defining the study area
fp_sa = '../data/region_hovedstaden.gpkg'
sa_layer_name ="region_hovedstaden"

#Filepath to polygon defining administrative boundaries
fp_adm = '../data/region_hovedstaden.gpkg'
adm_layer_name ="region_hovedstaden"

#Filepath to Corine land cover data
fp_lc = '../data/CLC12_DK.shp'
lc_layer_name = 'corine'

#Filepath to attribute data for Corine land cover
fp_att = '../data/clc_legend_modified.csv'

#Filepath to elevation model
fp_dem = '../data/DHM_10.tif'

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
ways_table = "ways_" + area_name
points_table = "points_" + area_name
rel_table = "rel_" + area_name
sa_table = "study_area_" + area_name
poly_table = "poly_" + area_name
lu_table = "land_use_" + area_name
adm_table = 'adm_boundary_' + area_name
