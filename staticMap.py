# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 20:07:56 2024

@author: mjwwr
"""
import requests
import streamlit as st
from io import BytesIO
""" 
============================get_mid_point==================================
INPUTS: Latitude array, longitude array
OUTPUTS: Midpoint between Latitudes and longitudes
Midpoint = (sum of latitides / 2) + (sum of longitudes / 2)
============================================================================
"""
def get_mid_point(latitude, longitude):
    lat_sum = 0
    longitude_sum = 0
    for item in latitude:
        lat_sum = lat_sum + item
    for item in longitude:
        longitude_sum = longitude_sum + item
    latitude_mid = lat_sum / 2
    longitude_mid = longitude_sum / 2
    
    mid_point_str = f'{latitude}, {longitude}'
    
    return mid_point_str

""" 
============================Get_STATIC_MAP==================================
INPUTS: API_KEY, CENTER, ZOOM, SIZE, MAPTYPE, AND MARKERS (OPTIONAL).
OUTPUTS: SAVED .PNG OF STATIC MAP
============================================================================
DESCIPTION: TAKES INPUTS TO MAKE AN HTTP REQUEST TO GOOGLE MAPS API.
INPUTS ARE PUT INTO PROPER PARAMETER FORMAT TO MAKE REQUESTS TO API.
REFER TO 
https://developers.google.com/maps/documentation/maps-static/start#Markers
TO MAKE CHANGES TO STATIC MAP
============================================================================
"""
def get_static_map(latitude, longitude):
    #Constants necessary to gett Static Map, api_key, marker set up, ect
    api_key = "AIzaSyClc025lr0s5Ofiv5ptTQC5AggtVe_rE5U"  
    #center = "42.665766929151644,-82.81108927939566"
    center = get_mid_point(latitude, longitude)
    
    zoom = "14"
    size = "500x500"
    maptype = "hybrid" 
    # Marker Org Here
   
    marker_str = marker_organizer(latitude, longitude)
    print(marker_str)
    
    # Construct the URL for the Google Static Maps API
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    
    # Parameters for the API request
    params = {
        "center": center,
        "zoom": zoom,
        "size": size,
        "maptype": maptype,
        "key": api_key
    }
    #If markers are present
    if marker_str:
           params["markers"] = marker_str
     
    # Make the API call
    #print (params)
    response = requests.get(base_url, params=params)

    # Saving image if test sucessful
    if response.status_code == 200:
        with open("static_map.png", "wb") as file:
            file.write(response.content)
        print("Map image saved as 'static_map.png'")
    else:
        print(f"Error: Unable to fetch the map. Status code: {response.status_code}")

def get_static_map_st(latitude, longitude):
    api_key = "AIzaSyClc025lr0s5Ofiv5ptTQC5AggtVe_rE5U"
    center = get_mid_point(latitude, longitude)

    max_dist = get_max_distance(latitude, longitude)
    zoom = get_zoom_from_distance(max_dist)

    size = "500x500"
    maptype = "hybrid"

    marker_str = marker_organizer(latitude, longitude)

    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    params = {
        "center": center,
        "zoom": zoom,
        "size": size,
        "maptype": maptype,
        "key": api_key
    }
    if marker_str:
        params["markers"] = marker_str

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        st.image(BytesIO(response.content), use_container_width=True)
    else:
        st.error(f"Error fetching map (status {response.status_code})")
""" 
==============================MARKER_ORGANIZER================================
INPUTS: MARKER LIST
OUTPUTS: PROPERLY FORMATTED MARKER STRING
==============================================================================
DESCIPTION: TAKES IN MARKER LIST AND FORMATS LIST TO ONE FORMAT STRING. 
THIS STRING IS FORMATTED EXACTLY HOW GOOGLE MAPS API DOCUMENTATION SPECIFIES. 
REFER TO 
https://developers.google.com/maps/documentation/maps-static/start#Markers
TO SEE MARKER FORMAT
==============================================================================
"""
def marker_organizer(latitude, longitude):
    markers = []
# https://ibit.ly/Ihlwd
    # Define markers (customize as needed)
    #Marker Set Up
    # marker1 = "color:blue|label:S|42.665766929151644,-82.81108927939566"
    n=0
    marker_str = ""
    for n, lat in enumerate(latitude):
        if n == 0:
           marker_str = f"color:blue|label:S|{lat},{longitude[n]}"
        else:
           marker_str = f"{marker_str}|{lat},{longitude[n]}"
    #markers.append(marker2)
    #set marker count
    # Check for bad data
    '''
    if markers == None:
        print('Error, please input value for markers')
    if not isinstance(markers, list):
        print('Error, please ensure input is in list format')
    '''
    # Format array into string
    '''
    for marker in markers:
        if j == 0:
            marker_str = marker
            j = j + 1
        else: 
            marker_str = f'{marker_str}\nmarkers= {marker}'
            j = j + 1
            '''
            
            
    return marker_str

""" 
============================GET_USER_LOC==================================
INPUTS: ZIP CODE (INT), STATE(STRING) NOTE: STATE IS 2 LETTER ABRV
OUTPUTS: LATIRUDE , LONGITUDE (FLOATS)
============================================================================
DESCIPTION: TAKES IN ZIP CODE AND STATE AND GETS APPROXIMAYTE USER LATITUDE 
AND LONGITUDE. USING FREE, PUBLIC API CALLED "zippopotam". MORE INFO CAN BE 
FOOUND HERE.
https://www.zippopotam.us/
============================================================================
"""
def get_user_loc(zip_code, state_code):
    """Returns the latitude and longitude for a given US zip code and state abbreviation."""
    url = f"http://api.zippopotam.us/us/{zip_code}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Validate state match
        place_state = data['places'][0]['state abbreviation']
        if place_state.upper() != state_code.upper():
            print(f"State code mismatch: expected {state_code}, got {place_state}")
            return None, None

        latitude = float(data['places'][0]['latitude'])
        longitude = float(data['places'][0]['longitude'])

        return latitude, longitude

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None, None
    except KeyError:
        print("Invalid response structure or ZIP not found.")
        return None, None        
        

from math import radians, cos, sin, sqrt, atan2
""" 
============================GET_USER_LOC==================================
INPUTS: 2 coordinate points as floats (lat, long)
OUTPUTS: distance between 2 coordinate points in miles (float)
============================================================================
DESCIPTION: Takes in a referenece latitude and longitude, then calculates 
distance from first coordinate point and second inputted coordinate point.
============================================================================
"""
def haversine_distance(lat1, lon1, lat2, lon2):
    """Returns distance in miles between two lat/lon points."""
    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
# This function filters through a latitude and longitude array to find the maxdistance between
# two coordinate points
def get_max_distance(latitudes, longitudes):
    max_dist = 0
    for i in range(len(latitudes)):
        for j in range(i + 1, len(latitudes)):
            dist = haversine_distance(latitudes[i], longitudes[i], latitudes[j], longitudes[j])
            if dist > max_dist:
                max_dist = dist
    return max_dist
# Get approximate zoom for google API
def get_zoom_from_distance(distance_miles):
    if distance_miles < 1:
        return "15"
    elif distance_miles < 5:
        return "13"
    elif distance_miles < 10:
        return "12"
    elif distance_miles < 25:
        return "10"
    elif distance_miles < 50:
        return "9"
    elif distance_miles < 100:
        return "7"
    elif distance_miles < 300:
        return "5"
    else:
        return "3"


"""        
if __name__ == "__main__":
    latitude_array = [42.40774437494314]
    longitude_array = [-83.07984484326032]
    get_static_map(latitude_array, longitude_array)
"""