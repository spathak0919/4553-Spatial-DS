import csv,json
from statistics import mean
import geopandas
from numpy import sort
from shapely.geometry import Point


with open('cities.geojson') as f:
    cities = json.load(f)

ufo = []

with open('ufo_data.csv') as f:         // open ufo data file
    csvfile = csv.DictReader(f, delimiter = ',')

    for row in csvfile:
     
        ufo.append(row)                 //csv in array

points = []
names = []

for feature in cities["features"]:
    if feature["geometry"]["type"] == "Point":
        points.append(feature["geometry"]["coordinates"])
        names.append(feature['properties']['city'])

cities = []
for point in points:
    cities.append(Point(point))


geo = geopandas.GeoSeries(cities)  // series of geo

output = []

for i in range(len(geo)):
    dist = []

    arr = geo.distance(geo[i])

    #converts result to an array
    arr = arr.values 

    for i in range(len(arr)):
        if arr[i] != 0:
          
            dist.append((names[i], arr[i])) // store all distances
    dist.sort(key= lambda x: x[1]) // nearest cities sort

    city = {
        'city': names[i],
        'longitude': geo[i].x,
        'latitude': geo[i].y,
        'distance': dist
    }

    output.append(city)
with open('distances.json', 'w') as f:
    f.write(json.dumps(output))

points = []
for dics in ufo:
    points.append(Point(float(dics['lon']), float(dics['lat'])))

geoufo = geopandas.GeoSeries(points)

output = []
for i in range(len(geo)):
    dist = []

    arr = geoufo.distance(geo[i])

    arr = arr.values
    arr = sort(arr)
    top = arr[0:100]

    #finds the average of the 100 closest ufos
    avg = round(mean(top), 18)

    city = {
        'city': names[i],
        'longitude': geo[i].x,
        'latitude': geo[i].y,
        'avgufo': avg
    }

    output.append(city)


with open('average_ufo.json', 'w') as f:  // average
    f.write(json.dumps(output))   
