'''
Configurations used in the analysis
'''

#Name of study area
area_name = 'dk'

#Filepath to polygon defining the study area
fp_sa = r'C:\Users\OA03FG\OneDrive - Aalborg Universitet\AAU DATA\AAU GeoDATA\denmark.gpkg'
sa_layer_name ="boundary"

#Filepath to Corine land cover data
fp_lc = r'C:/Users/OA03FG/OneDrive - Aalborg Universitet/AAU DATA/AAU GeoDATA/DK_CORINE_SHP_UTM32-WGS84/CLC06_DK.shp'
lc_layer_name = 'corine'

#Filepath to attribute data for Corine land cover
fp_att = r'C:/Users/OA03FG/Aalborg Universitet/Urban Research group - General/AAU data/AAU grunddata/PROTOTYPE/clc_legend_modified.csv'

#Size of buffer in metres
buffer = 3000

# Define CRS
crs = 25832

# Database connection
db_user = 'postgres'
db_password = 'AAU20'
db_host = 'localhost'
db_name = 'dk'
db_port = '5432'

#Setting table names
ways_table = "ways" + area_name
points_table = "points" + area_name
rel_table = "rel" + area_name
sa_table = "study_area" + area_name
poly_table = "poly" + area_name
lu_table = "land_use" + area_name
