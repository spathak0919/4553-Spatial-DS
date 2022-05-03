# Author: Sandesh Pathak
# Assignment: P08
# Description: To Create a geoJson file, goal is to color each state based on the population in cities.json.

## Summary of program works : Program reads cities.json which has lat/long/population and reads states as well. It checks lat/long is within boundary of 
##                            coordiantes of the state. If yes it will get the population.
##                            Colors were assigned to each population state #067737 (blue color) 
##                           

import json

## adding cities
def append_color(state_data, state_population):

    color_tinit_list = ["#e6f1fb","#cde3f7","#b4d6f3","#9bc8ef","#82bbeb","#69ade7","#509fe3","#3792df","#1e84db","#0677d7"]
    #divide the states into 10 segments and assign color to each segment:
    
    #population_segment = {'66318': '#e6f1fb', '2998931': '#cde3f7', '5931544': '#b4d6f3', '8864157': '#9bc8ef', '11796770': '#82bbeb', '14729383': '#69ade7', '17661996': '#509fe3', '20594609': '#3792df', '23527222': '#1e84db', '29392452': '#0677d7'}
    state_color = {}
    
    count = 0
    main_count = 0
    states = state_population.keys()
    print(len(states))
    
    for state in states:
        if(count == 5):
            
            main_count+=1
            state_color[state] = color_tinit_list[main_count]
            print(main_count)
            count = 0
        else:
            
            state_color[state] = color_tinit_list[main_count]
            count = count+1

    count = 0
    for state in state_color:
        count+=1
        print(state," ",state_color[state])
    
    for i in range(0,len(state_data["features"])):
        for state in state_color:
            if state_data["features"][i]["id"] == state:
                state_data["features"][i]["properties"]["Population"] = state_population[state]
                state_data["features"][i]["properties"]["stroke"] = "#555555"
                state_data["features"][i]["properties"]["stroke-width"] = 2
                state_data["features"][i]["properties"]["stroke-opacity"] =1
                state_data["features"][i]["properties"]["fill"] = state_color[state]
                state_data["features"][i]["properties"]["fill-opacity"] = 0.75
                state_data["features"][i]["properties"]["type"] = "state"
    return state_data

def check_state(city_coord, state_poly_coords):
    
    state_poly_coord_list = []
    for poly in state_poly_coords:
        for sub_poly in poly:
            for lat_long in sub_poly:
                if(str(type(lat_long)) == "<class 'list'>"):
                    #print(lat_long)
                    #convert neg to pos and append
                    lat_long = [abs(lat_long[0]), abs(lat_long[1])]
                    state_poly_coord_list.append(lat_long)
                else:
                    #print(sub_poly)
                    #convert neg to pos and append
                    sub_poly = [abs(sub_poly[0]), abs(sub_poly[1])]
                    state_poly_coord_list.append(sub_poly)

    ## check min lat and min long of state 
    #min lat
    min_lat = min(state_poly_coord_list, key = lambda x: x[0])[0]
    
    #min long
    min_long = min(state_poly_coord_list, key = lambda x: x[1])[1]
    

    #max lat
    max_lat = max(state_poly_coord_list, key = lambda x: x[0])[0]
    
    #max long
    max_long = max(state_poly_coord_list, key = lambda x: x[1])[1]
    
    #convert city coord to positive as well and switch from lat long to long lat as geogson file has long lat
    city_coord = [abs(city_coord[1]), abs(city_coord[0])]

    #if city lat and long are within the poly coordinates then return true
    if((city_coord[0] >= min_lat) and (city_coord[0] <= max_lat) and (city_coord[1] >= min_long) and (city_coord[1] <= max_long)):
        return True
    else:
        return False
    

def main():

    # read form cities.json
    city_data = {}
    with open("cities.json", 'r') as f:
        city_data = json.load(f)
     
    # read from states.geojosn 
    state_data = {}
    with open("states.geojson", 'r') as f:
        state_data = json.load(f)
    # coordinates are mapped 
    state_coords = {}
    for feature in state_data["features"]:
        state_coords[feature["id"]] = feature["geometry"]["coordinates"]

    state_population = {}
    #checking which city is in which state:
    print(len(state_coords))
    for city in city_data:
       
        ## lat/long was checked in the state
        for state in state_coords:
            check = check_state([city['latitude'], city['longitude']], state_coords[state])
            if(check):
                #city is within state so add to state population
                try:
                    state_population[state] +=city["population"]
                except:
                    state_population[state]  = city["population"]
                break
    for state in state_coords:
        if state not in state_population:
            print(state)
            state_population[state] = 0           
    sorted_pop = {k: v for k, v in sorted(state_population.items(), key=lambda item: item[1])}

    geo = append_color(state_data,sorted_pop)
    with open('Output.geojson', 'w') as f:
        json.dump(geo, f, indent=4)
main()
