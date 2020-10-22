'''
Configurations used in the analysis
'''

#Name of study area
area_name = 'kbh'

#Filepath to polygon defining the study area
fp_sa = r"C:\Users\viero\OneDrive\Documents\AAU\AAU_Geodata\cph.gpkg"
layer_name ="Copenhagen_boundary"

#Size of buffer in metres
buffer = 200

# Define CRS
crs = 25832

# Database connection
db_user = 'postgres'
db_password = 'IGEON20'
db_host = 'localhost'
database_name = 'proto'
db_port = '5432'