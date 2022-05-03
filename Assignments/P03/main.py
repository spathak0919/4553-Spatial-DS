
## USING TRANSFORMER 
## OUTPUT JSON

# import numpy as np
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import pyproj
import random
import shapely.geometry
import sys
from pyproj import Transformer
import json

from geovoronoi import voronoi_regions_from_coords, points_to_coords
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
from shapely.ops import unary_union

# from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import transform

# read cities points into geodata frames
cities = gp.read_file("cities.geojson")

# read border points into geodata frames
us_border = gp.read_file("us_nation_border.geojson")


# read ufo points into geodata frames
ufos = gp.read_file("ufo_data.geojson")

#makes geopandas dataframe from ufo
#crs projects points
us_border = us_border.to_crs(epsg=3395)
shape = unary_union(us_border.geometry)

cities = cities.to_crs(epsg=3395)

geometry = points_to_coords(cities.geometry)


regions, rPts = voronoi_regions_from_coords(geometry, shape)

ufos = ufos.to_crs(epsg=3395)
uInd = gp.GeoSeries(ufos["geometry"])
cty = cities["city"]
cty = cities["city"]

# store ufo
ufoReg = []

# transformer reproject points
transformer = Transformer.from_crs("epsg:3395", "epsg:4326")

# iterate through the polygon of multipolygon 
# external coordinates of polygon
for i in range(len(regions)):
    city = {"Region": i, "City": cty[i], "UFOs": []}
    region = uInd.within(regions[i])

    for j in range(len(region)):
        if region[j]:
            ufo_data = transformer.transform(ufos["geometry"][j].x, ufos["geometry"][j].y)
            ufo_data = tuple([round(x, 4) for x in ufo_data])
            city["UFOs"].append({j: ufo_data})
    ufoReg.append(city)

# writing output to file
with open("cityResults.json", 'w') as wr:
    wr.write(json.dumps(ufoReg))

