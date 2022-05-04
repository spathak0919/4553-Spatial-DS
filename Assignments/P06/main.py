import geopandas as gdp 
import json  
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
import pandas as pd
import math
from fastapi.middleware.cors import CORSMiddleware 
from math import radians, cos, sin, asin, sqrt

from shapely.geometry import Polygon 


                                                                                 
class Spatial:
    def __init__(self): 
    
        ##OPEN FILES

        try:
            with open('countries.geojson') as infile:
                self.DataWorld = json.load(infile)
            
        except IOError:
            print('ERROR')
        
        try: 
      
            self.output = open('output.geojson', 'w')
        except IOError:
     
            print("ERROR")

    def getCountryList(self): 

        DictList=[] 
        for feature in self.DataWorld['features']:
            
            DictList.append(feature['properties']['name'])
        return(DictList) 

    def getPolyGon(self,name): 

        for feature in self.DataWorld['features']:
           
            if(feature['properties']['name']== name):
                print("COUNTRY NAME : ",name, " COORDINATES ARE :\n\n",
                feature['geometry']['coordinates']) 
                
            coordinates=feature['geometry']['coordinates']
            return coordinates 


     
    def GetCenterPoint(self, name): 
        coordinate=[]
        df1 = pd.read_csv('countries.csv')
        
        df1.drop(['ISO','COUNTRYAFF','AFF_ISO'], axis=1,inplace=True)
        print(df1)
        
        for i in range(len(df1.COUNTRY)):\
            # for the length of the file

            if name == df1['COUNTRY'][i]: 
                # LAT/LONG

                XVal=df1['longitude'][i] 
                YVal=df1['latitude'][i]  
                coordinate.append((XVal,YVal))

        return XVal,YVal

    
    def importcontinent(self, name): 
            # read file
        df2 = pd.read_csv('continents.csv')
        for i in range(len(df2.Country)): 
            if name == df2['Country'][i]:  
               continent= df2['Continent'][i] 

        return continent 
                
        ## GET DISTANCE

    def distance(self, Country1, Country2):
        CountryDist=[]
        CountryDist.append(Country1)
        CountryDist.append(Country2)

        for (x1, y1), (x2, y2) in zip(CountryDist, CountryDist[1:]):
        
            x1, y1, x2, y2 = map(radians, [x1, y1, x2, y2])
            # haversine formula

            dlon = x2 - x1
            dlat = y2 - y1
            a = sin(dlat/2)**2+cos(y1)*cos(y2)*sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371
            ## converting to miles

            value= (c * r)/1.609
        return value
        

                # to find direction of country
                #  
    def direction(self, FirstCountry, SecondCountry):

            #create empty
        CountryDistance=[] 
        
        CountryDistance.append(FirstCountry) 
        CountryDistance.append(SecondCountry) 

        for (x1, y1), (x2, y2) in zip(CountryDistance, CountryDistance[1:]): 
            # create some if statements to handle positioning
            # locating directions

            if x1 < x2 and y1 > y2:
                CountryDirection = 'NorthWest' 
            elif x1 > x2 and y1 > y2:
                CountryDirection = 'NorthEast'
            elif x1 < x2 and y1 < y2:              
                CountryDirection = 'SouthWest' 
            elif x1 > x2 and y1 < y2:
                CountryDirection = 'SouthEast' 

                #IF/ELSE STATEMENT

            else:
                if x1 == x2 and y1 > y2:
                    CountryDirection = 'North' 
                elif x1 == x2 and y1 < y2:
                    CountryDirection = 'South' 
                elif x1 < x2 and y1 == y2:
                    CountryDirection = 'East'  
                elif x1 > x2 and y1 == y2:
                    CountryDirection = 'West'  
               
        return CountryDirection 

    def geojson(self,name):
        for feature in self.DataWorld['features']:
            
            if(feature['properties']['name']== name):
                print("The name of the country is : ",name, " the coordinates are :\n\n",feature['geometry']['coordinates'])
                coordinates=feature['geometry']['coordinates']
                

                if(feature['geometry']['type']=='Polygon'):
                    
                    OutFile = {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    OutFile['features'].append({
                                "type": "Feature",
                                "properties": {},
                                "geometry": {
                                "type": "Polygon",
                                "coordinates": 
                                    coordinates 
                                }
                            })
                else:
                    OutFile = {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    OutFile['features'].append({
                                "type": "Feature",
                                "properties": {},
                                "geometry": {
                                "type": "MultiPolygon",
                                "coordinates": 
                                    coordinates 
                                }
                            })
    # write to the ouput file

                self.output.write(json.dumps(OutFile, indent=4))
                
                return OutFile
        
    
                        ##GETTING API TO WORK

if __name__ == '__main__':
    uvicorn.run("main:HelperApi",host="127.0.0.1", port=8080, log_level="debug", reload=True)
    
    
ImportedData = Spatial()

origins = ["*"]

description = """
## Worldle Clone
### With Better Distance Calculations
"""


HelperApi = FastAPI(title="Worldle Clone",
    description=description,
    version="0.0.1",
    terms_of_service="http://killzonmbieswith.us/worldleterms/",
    contact={
        "name": "Worldle Clone",
        "url": "http://killzonmbieswith.us/worldle/contact/",
        "email": "chacha@killzonmbieswith.us",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },)# getting our api running
# Needed for CORS
HelperApi.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
                                                                           
#path through the api that leads to all the doc files inside of the requester root directory
@HelperApi.get('/')
async def RootFolder():# create a root folder for all the documents grabbed by the api
    return RedirectResponse(url="/docs")# direct response to the documents folder ending in docs




##  retrieve the countires

@HelperApi.get('/CountryList/') 
async def countries(): 
    countries = ImportedData.getCountryList() 
    OutPut = {'detail': 'Success','countries': countries} 
    return OutPut 


#FIND POLYGON OF COUNTRY
#                                                          
@HelperApi.get('/FindPolyGon/{country}')
async def PolyGon(country: str): 
    country = country.title() 
    country = ImportedData.getPolyGon(country) 
    OutPut = {'PolyGon for Country': country}
    return OutPut


# FIND CONTINETNT
                                                                         
@HelperApi.get('/FindContinet/{country}')
async def ContinentLocator(country: str): 
    Continent = ImportedData.importcontinent(country) 
    OutPut = {'Country Continent': Continent} 
    return OutPut# return the result

                                                                                                               
@HelperApi.get('/FindCenter/{country}')
async def Country_Center(country: str): 
    CountryCenter = ImportedData.GetCenterPoint(country) 
    OutPut = {'Country Center': CountryCenter}
    return OutPut
             
## FIND Distance between the polygons

@HelperApi.get('/FindDistance/{FirstCountry},{SecondCountry}')
async def Country_Distance(FirstPoly: str, SecondPoly: str):

    Country1= ImportedData.GetCenterPoint(FirstPoly)
    Country2= ImportedData.GetCenterPoint(SecondPoly)
    DistanceBetween = ImportedData.distance(Country1, Country2)
    OutPut = {'distance': DistanceBetween}
    return OutPut


@HelperApi.get('/FindDirection/{Country1},{Country2}')
async def CountryDirection(CountryNo1: str, CountryNo2: str):
    # input the two countries calling the get centerpoint
    FirstCountry= ImportedData.GetCenterPoint(CountryNo1)
    SecondCountry= ImportedData.GetCenterPoint(CountryNo2)
    # call the method to find the distance
    DirectionToCountry = ImportedData.direction(FirstCountry,SecondCountry)
    # return the method back
    OutPut = {'CountryDirection': DirectionToCountry}
    return OutPut
                                                                          

@HelperApi.get('/Geojson/{country}')
async def GeoJson(country: str):
    OutPut = ImportedData.geojson(country) 




