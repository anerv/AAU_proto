'''
Configurations used in the analysis
'''

#Name of study area
area_name = 'kbh'

#Filepath to polygon defining the study area
fp_sa = r""
layer_name ="Copenhagen_boundary"

#Size of buffer in metres
buffer = 150

# Define CRS
crs = 25832

# Database connection
db_user = 'postgres'
db_password = 
db_host = 'localhost'
db_name = 'cphbike'
db_port = '5432'

#Setting table names
ways_table = "ways" + area_name
points_table = "points" + area_name
rel_table = "rel" + area_name
sa_table = "study_area" + area_name

