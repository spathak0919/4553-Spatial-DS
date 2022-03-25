# PO3: Vornoi- Real World Use Case

### The voronoi diagram, allows us to create polygons around each city to use as "ufo containers". . Voronoi diagrams create polygons around "seeds" (cities in our case) such that the lines making up each polygon are equidistant between any two given cities. 


|   #   | File Link       | Assignment Description              |  
| :---: | --------------  | --------------------------------    |
|     1 | main.py         |                                   |
|    2  | cities.geojson  | cities                              |
|     4 | ufodata.csv     | ufo data                            |
|     5 | BetterUFOData.csv  | states                              |
|     6 | distance.csv    | distance between cities             |
|     7 | avg.json        | average                             |

###  Requirements
1.  Create a voronoi diagram over the US creating polygons around each of the 49 cities.
2.  Load said polygons into a spatial tree (geopandas rtree).
3.  Load each of the UFO sighting points into the same rtree.
4.  Query the rtree getting the UFO sighting points that are contained within each polygon.
5.  Save your results to a json file.


