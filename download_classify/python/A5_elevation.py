'''
This scripts calculates the elevation profile for cycling infrastructure based on a DEM
The method uses a DEM with a resolution of at least 5*5 meters
The raster is loaded to the database using raster2pgsql, but use the code below to check that the raster has the correct format
'''

#%%
#Importing modules
import rasterio
from rasterio.enums import Resampling
from config import *
from database_functions import *
#%%
'''
upscale_factor = 2

raster = rasterio.open(fp_dem)


    # resample data to target shape
data = raster.read(
    out_shape=(
        raster.count,
        int(raster.height * upscale_factor),
        int(raster.width * upscale_factor)
    ),
    resampling=Resampling.bilinear
)

# scale image transform
transform = raster.transform * raster.transform.scale(
    (raster.width / data.shape[-1]),
    (raster.height / data.shape[-2])
)
'''
# %%
# Read raster
dem = rasterio.open(fp_dem)
# %%
#Check resolution
pixel_x, pixel_y = dem.res
if pixel_x >= 4.99 and pixel_y >= 4.99:
    print('The DEM resolution is okay')
else:
    print('This script requires a resolution of 5*5 meters or larger')
#%%
#Check crs
if dem.crs == crs:
    print('The DEM is in the right projection')
else:
    print('Please reproject DEM to EPSG:%d' % crs)
# %%
# %%

