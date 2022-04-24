# Author: Sandesh Pathak
# Assignment: P01
# Description: Input file cities.json, Largest cities in every state not including Hawai and Alaska

import json
import random


# Change path as appropriate
with open("cities.json") as f:
  data = json.load(f)

# color for largest cities
def randColor():
  r = lambda: random.randint(0,255)
  return ('#%02X%02X%02X' % (r(),r(),r()))

 
def cityToPointFeature(city):
  # create an empty feature dictionary
  feature = {
    "type": "Feature",
    "properties": {
    "marker-color":randColor(),
    },
    "geometry": {
    "type": "Point",
    "coordinates": [0,
      0,0
      ]
    }
  }
  
  # loop over our city dictionary
  # adding items to correct place
  for key,val in city.items():

    # if longitude in key make it the first item in coordinates
    if key == 'longitude':
      feature['geometry']['coordinates'][0] = val

    # likewise, make latitude the second item in coordinates
    elif key == 'latitude':
      feature['geometry']['coordinates'][1] = val

    # everything else gets put into properties
    else:
      feature['properties'][key] = val

  return feature
  


states = {}

for item in data:
  if not item["state"] in states:
    states[item["state"]] = []

  states[item["state"]].append(item)

# we filter out Alaska and Hawaii.
  
filterlist = []

for state,stateInfo in states.items():
  filter=-1
  hipopcity = {}
  for i in range(len(stateInfo)):
    if stateInfo[i].get('population') > filter:
      filter = stateInfo[i].get('population')
      filtercity = stateInfo[i]
  filterlist.append(filtercity)

points = []
linecoords = []

#if cities greater than 125 it includes hawii and alaska so cities less than -125
for city in filterlist:
  if city['longitude'] > -125: 
    points.append(cityToPointFeature(city))
    linecoords.append([city['longitude'],city['latitude']])

def sortlong(val):
  return val[0]

linecoords.sort(key=sortlong)

linestr = {
  "type": "Feature",
  "properties": 
  {
    "color": randColor()
  },
  "geometry": {
    "type": "LineString",
    "coordinates": []
  }
}
# Rank cities from West to East and Lines are drawn from west to east

self_geo = {
  "type": "FeatureCollection",
  "features": []
}

for city_item in points:
 
  self_geo['features'].append(city_item)
for coord in linecoords:
  linestr["geometry"]["coordinates"].append(coord)
self_geo['features'].append(linestr)

#output file 
with open("output.geojson","w") as f:
  json.dump(self_geo,f,indent=4)
