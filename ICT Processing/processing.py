import rasterio
from rasterio.plot import show
import rasterio
from rasterio.features import shapes
import geopandas as gpd
import xarray
import numpy as np

def raster_file_to_gdf(fname, tolerance = 0.00005, label_val = 1,  crs = "EPSG:4326"):
     with rasterio.Env():
        with rasterio.open(fname) as src:
            image = src.read(1) # first band
            results = (
                {'properties': {'raster_val': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    shapes(image, mask = None, transform = src.transform)) if v == label_val)

            df = gpd.GeoDataFrame.from_features(list(results)).simplify(tolerance = tolerance)
            df.crs = crs
            
            return df

def raster_to_gdf(array, transform, tolerance = 0.00005, label_val = 1,  crs = "EPSG:4326"):
    results = ({'properties': {'raster_val': v}, 'geometry': s} for i, (s, v) in enumerate(shapes(array.astype(np.int16), mask = None, transform = transform)) if v == label_val)
    labels = gpd.GeoDataFrame.from_features(list(results)).simplify(tolerance = tolerance)
    labels.crs = crs

    return  labels

def get_gpd_area(gdf, units = 'km'):
    if units == 'm':
        return (gdf.to_crs({'proj':'cea'}).area).sum()
    elif units == 'km':
        return (gdf.to_crs({'proj':'cea'}).area / 10**6).sum()