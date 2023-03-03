import xarray
import distancerasters as dr
import rasterio
import cv2
import numpy as np

def ndvi(nir, red):
    return ((nir - red) / (nir + red))

def ndwi(nir, green):
    return ((green - nir) / (green + nir))

def s2_ndvi(raster):
    if isinstance(raster, xarray.Dataset):
        red = raster.B04
        nir = raster.B08
    elif isinstance(raster, rasterio.DatasetReader):
        red = raster.read(8)
        nir = raster.read(4)
    else:
        return None

    return ndvi(nir, red)



def s2_ndwi(raster):
    if isinstance(raster, xarray.Dataset):
        nir = raster.B08
        green = raster.B03
    elif isinstance(raster, rasterio.DatasetReader):
        nir = raster.read(8)
        green = raster.read(3)
    else:
        return None
    
    return ndwi(nir, green)
    
def s2_vegetation_mask(raster, threshold = 0.2):
    return (s2_ndvi(raster) > threshold)
    
def s2_water_mask(raster, threshold = 0):
    return (s2_ndwi(raster) > threshold)
    
def s2_distance_to_water(raster, threshold = 0):
    water_mask = s2_water_mask(raster, threshold = threshold)

    #Applying a blur, otherwise small puddles and ponds/noise would be classified as water
    water = cv2.GaussianBlur(water_mask.to_numpy().astype(np.uint8), (0,0), sigmaX=5, sigmaY=5)
    dist =  dr.DistanceRaster(water).dist_array
    return xarray.DataArray(dist, coords={'y': water_mask.coords['y'],'x': water_mask.coords['x'], 
                                          'spatial_ref': water_mask.coords['spatial_ref']}, 
                                          dims=["y", "x"])