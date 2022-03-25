# PO3: Vornoi- Real World Use Case

### The voronoi diagram 
Allows us to create polygons around each city to use as "ufo containers". . Voronoi diagrams create polygons around "seeds" (cities in our case) such that the lines making up each polygon are equidistant between any two given cities. 


|   #   | File Link       | Assignment Description              |  
| :---: | --------------  | --------------------------------    |
|     1 | main.py         | process json files                            |
|    2  | cities.geojson  | cities                              |
|     3 | ufodata.csv     | ufo data                            |
|     4 | BetterUFOData.csv  | states                              |
|     5 |us_border_shp   | shapes            |


###  Requirements
1.  Create a voronoi diagram over the US creating polygons around each of the 49 cities.
2.  Load said polygons into a spatial tree (geopandas rtree).
3.  Load each of the UFO sighting points into the same rtree.
4.  Query the rtree getting the UFO sighting points that are contained within each polygon.
5.  Save your results to a json file.


