import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import json
from pyproj import Transformer



from shapely.ops import unary_union
# from shapely.geometry import Polygon, mapping
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
from geovoronoi import voronoi_regions_from_coords, points_to_coords
from shapely.ops import transform

debug = True
spatIndex = None

# ufodf = pd.read_csv("data/ufo_data.csv")

#loads cities/points into geodatframes
citiesgdf = gpd.read_file('cities.geojson')



ufodata = pd.read_csv('BetterUFOData.csv')

pd.set_option('display.max_columns', None)

#makes geopandas dataframe from ufo
#crs projects points
ufogdf = gpd.GeoDataFrame(ufodata, geometry = 
    gpd.points_from_xy(ufodata.lon, ufodata.lat), crs = "EPSG:4326")
    
ufogdf = ufogdf.to_crs(epsg =3395)


#open shape file as geopandas dataframe for borders/outline
border = gpd.read_file('us_border_shp')



#create subplot
fig, ax = plt.subplots(figsize =(12, 10))

#plots border
border.plot(ax=ax, color = "gray")

#plots city / points 
citiesgdf.plot(ax=ax, markersize=2.5, color = "blue")
ax.axis("off")
plt.axis('equal')


#CREATE VORONOI DIAGRAM

#ensure coords are correct projection time
#to_crs returns geoseries with all geometries tranformed
#to new coordinate reference system
#epsg : specifies output projection
border = border.to_crs(epsg=3395)
citiesgdf_proj = citiesgdf.to_crs(border.crs)

#convert points to coords
border_shape = unary_union(border.geometry)
coords = points_to_coords(citiesgdf_proj.geometry)
# print(coords)

#create the polygon etc
region_polys, region_pts = voronoi_regions_from_coords(coords,border_shape)

fig, ax = subplot_for_map(figsize= (12, 10))

# create/plot voronoi diagram
plot_voronoi_polys_with_points_in_area(ax, border_shape, region_polys, coords, region_pts)

#shows voronoi and borders/boundary & cities
fig  = plt.gcf()
#saves voronoi fig
fig.savefig('voronoi1.png')
plt.show()




#ufogdf contains lon, lat, geometry/points
#spatialIdx now contains index and points from ufodata
spatialIdx = gpd.GeoSeries(ufogdf["geometry"])

#stores result of city 
cityDictResults = [] 

#transforms reprojects points 
transformer = Transformer.from_crs("epsg:3395", "epsg:4326")


for i in range(len(citiesgdf)):

    cityDict = { "city" : citiesgdf["city"][i],
                 "polygon": [],
                 "ufos": [] 
                 }

    #runs a query looking for ufo's within the polygon
    results = spatialIdx.within(region_polys[i])
    
    for j in range(len(results)):
        if results[j]:
            cityDict["ufos"].append([ufodata["geometry"][j].x, ufodata["geometry"][j].y])

    #THERE ARE SINGLE AND MULTIPOLYGON HENCE YOU NEED TO ITERATE THROUGH
    #THE POLYGONS OF THE MULTIPOLYGON TO GET THE EXTERIOR CORRDS OF EACH
    #POLYGON
    if region_polys[i].geom_type == 'Polygon':
        for x,y in region_polys[i].exterior.coords:
            x1,y1 = transformer.transform(x,y)
            cityDict["polygon"].append([x1,y1])

    elif region_polys[i].geom_type == 'MultiPolygon':
        points = []
        pointstoList = []
        
        for polygon in (region_polys[i]):
            #gets the exterior coords of each polygon
            points.extend(polygon.exterior.coords[:-1])
            #convert list of tuples to list of list
            pointstoList = list(map(list, points))
            #extracting x,y coordinates from each list
            for x, y in pointstoList:
                #reprojecting points
                x1,y1 = transformer.transform(x,y)
                #appending reprojected points to polys 
                cityDict["polygon"].append([x1,y1])
    
    cityDictResults.append(cityDict)       
    
#writing output to file
with open("Output.json", 'w') as wr:
    wr.write(json.dumps(cityDictResults))

 
