'''
This scripts calculates the elevation profile for cycling infrastructure based on a DEM
The method uses a DEM with a resolution of at least 10*10 meters
'''

#%%
#Importing modules
import rasterio
from rasterio.enums import Resampling
from config import *
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
if pixel_x >= 10 and pixel_y >= 10:
    print('The DEM resolution is okay')
else:
    print('This script requires a resolution of at least 10*10 meters')
#%%
#Check crs
if dem.crs == crs:
    print('The DEM is in the right projection')
else:
    print('Please reproject DEM to EPSG:%d' % crs)
# %%
