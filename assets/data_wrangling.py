import warnings
warnings.simplefilter(action='ignore')
import pandas as pd
import numpy as np
import geopandas as gpd
import requests
import os
import pickle
import osmnx as ox
import re
from time import time
import json
import logging
import geojson
from pathlib import Path
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
from scipy import spatial
from opencensus.ext.azure.log_exporter import AzureLogHandler
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=d989e5c0-698b-4b3e-a645-18ac1f273b59')
)


cwd = Path().resolve()

class DataManipulation():
    def __int__(self):
        self.cwd = Path().resolve()
        print(" ")


    def get_geo_data(self):
        """ load geojson data """
        with open(os.path.join(Path(cwd), 'data', 'geojson', 'vienna.geojson'), encoding='utf-8') as fp:
            counties = geojson.load(fp)
        return counties


    def parse_input(self, text):
        """ parse input and return Point(lat,lon)
        e.g. Universitätsring 2, Wien -> to POINT(lat/long)
        """
        try:
            data_json = requests.get(url=f'https://nominatim.openstreetmap.org/search?q={text}&format=json&polygon=1&addressdetails=1').json()
            lat = data_json[0]['lat']
            lon = data_json[0]['lon']
            df = pd.DataFrame({'Location':[text]})
            gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_xy([lon], [lat], crs=self.get_local_utm_crs()))
            return gdf
        except Exception as e:
            print(e)
            logger.exception(f'parse input: {e}')


    def get_tree(self, df):
        """ get spatial KDtree"""
        try:
            coords = list(zip(df.geometry.apply(lambda x: x.y).values, df.geometry.apply(lambda x: x.x).values))
            tree = spatial.KDTree(coords)
            return tree
        except Exception as e:
            print(e)


    def find_points_closeby(self, tree, lat_lon, k=500, max_distance=500):
        """ find points of interest in a 500 meter radius """
        results = tree.query((lat_lon), k=k, distance_upper_bound=max_distance)
        zipped_results = list(zip(results[0], results[1]))
        zipped_results = [i for i in zipped_results if i[0] != np.inf]
        return len(zipped_results)


    def get_region(self):
        """  """
        boundary_geojson = gpd.read_file(os.path.join(Path(cwd), 'data', 'geojson', 'vienna.geojson'))
        boundary_geojson.drop(columns=['cartodb_id', 'created_at', 'updated_at'], inplace=True)
        region = boundary_geojson.geometry.unary_union
        return region


    def get_local_crs(self, y, x):
        """ get local crs """
        x = ox.utils_geo.bbox_from_point((y, x), dist=500, project_utm=True, return_crs=True)
        return x[-1]


    def get_local_utm_crs(self):
        """ Set longitude and latitude of Vienna """
        lon_latitude = 48.210033
        lon_longitude = 16.363449
        local_utm_crs = self.get_local_crs(lon_latitude, lon_longitude)
        return local_utm_crs


    def get_model(self):
        """ load model from .pkl file """
        with open(os.path.join(Path(cwd), 'model', 'xboost.pkl'), 'rb') as f:
            model = pickle.load(f)
        return model


    def get_lat_long(self, point):
        """ get latitude and longitude coordinate from POINT geometry """
        try:
            return pd.Series([point.x, point.y])
        except Exception as e:
            pass


    def geo_coordinates(self, df):
        """ import from csv in geopandas dataframe
        source: https://stackoverflow.com/questions/61122875/geopandas-how-to-read-a-csv-and-convert-to-a-geopandas-dataframe-with-polygons
        """
        df['geometry'] = df['geometry'].apply(lambda x: x.centroid if type(x) == Polygon else (x.centroid if type(x) == MultiPolygon else x))
        df[['long', 'lat']] = df.apply(lambda x: self.get_lat_long(x['geometry']), axis=1)
        df = df[df['geometry'].apply(lambda x : x.type=='Point')]
        df = df.to_crs(self.get_local_utm_crs())
        return df


    def import_csv_to_gpd(self, name):
        """ import the csv file a gepandas dataframe """
        df = pd.read_csv(os.path.join(Path(cwd), 'data', 'osm', f'{name}.csv'), sep=",", usecols=['osmid', 'geometry'])
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
        return self.geo_coordinates(gdf)


    def check_if_coord_in_poly(self, region, long, lat):
        """
        Check if a coordinate (lat,long) is within a given polygon
        Used to check for an address in vienna geometry
        source: https://stackoverflow.com/questions/48097742/geopandas-point-in-polygon
        Return: True if Point within Polygon
        """
        _pnts = [Point(long, lat)]
        poly = gpd.GeoSeries({'within': region})
        pnts = gpd.GeoDataFrame(geometry=_pnts, index=['Point to check'], crs=self.get_local_crs(16.363449, 48.210033))
        pnts = pnts.assign(**{key: pnts.within(geom) for key, geom in poly.items()})
        return pnts['within'].item()


    def predict_price(self, df, parameters, names):
        """ predict price based on osm features """
        try:
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs=4326)
            df = df.to_crs(self.get_local_utm_crs())
        except Exception as e:
            print(f'gpd.GeoDataFrame: {e}')
        for name, i in zip(names, parameters):
            tree = self.get_tree(i)
            df[name] = df.apply(lambda row: self.find_points_closeby(tree, (row.geometry.y, row.geometry.x)), axis=1)

        # todo: supermarkets are not considered yet.
        # todo: change hard coded column numbers
        return df.iloc[:, 4:-2]


    def import_data(self):
        """ return (import) the airbnb data frame """
        return pd.read_csv(os.path.join(Path(cwd), 'data', 'airbnb_dataframe.csv'), encoding='utf-8')