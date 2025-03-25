# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 03:11:54 2025

@author: mjwwr
"""

import firebase_admin
from firebase_admin import credentials, db
import requests
import json
from datetime import datetime
import random
"""
====================================================================
========================ICE_REPORT_DATABASE=========================
INPUTS: API KEY(S), LONGITUDE, LATITUDE, ICE_DETECTED
OUTPUTS: JSON OF MEASYURED DATA FROM NEAREST NOAA CENTER, POST TO
REALTIME DATABASE IN GOOGLE FIREBASE.
====================================================================
DESCRIPTION: THIS FUNCTION GETS LIVE DATA FROM NEAREST NOAA STATION 
AVAILABLE, FROM HERE WE ORGANIZE DATA FROM NOAA AND POST A JSON OF
DATA VALUABLE TO OUR NN MODEL TO TRAIN. THIS CODE WILL BE RAN IN 
OUR REPORTING LOOP WHERE WE HAVE AN ARRAY OF ICE REPORTS. IF THE 
ARRAY IS EMPTY, THEN THERE IS NO ICE TO REPORT.
====================================================================
====================================================================
""" 
def fetch_noaa_data(api_key,latitude,longitude,fetch = None):
    url = f'https://api.weather.gov/points/{latitude},{longitude}'
   # print
    headers = {'token': api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    if fetch == None:     
       url = url
    else:
       url = data.get('properties').get(f'{fetch}')
    headers = {'token': api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def fetch_weather(api_key, location):
   
    url = f'https://api.weatherapi.com/v1/current.json?&key={api_key}&q={location}'
    response = requests.get(url)
    data = response.json()
    return data
#['current'], data['forecast']['forecastday']


"""
====================================================================
==========================FECTH_LIVE_DATA===========================
INPUTS: API KEY, LONGITUDE, LATITUDE
OUTPUTS: JSON OF MEASYURED DATA FROM NEAREST NOAA CENTER
====================================================================
DESCRIPTION: THIS FUNCTION GETS LIVE DATA FROM NEAREST NOAA STATION 
AVAILABLE, FROM HERE WE CAN SEE ALL MEASURED VALUES IN JSON FORMAT.
USES fetch_noaa_data FUNCTION TO FETCH NEAREST OBSERVATION STATIONS.
====================================================================
====================================================================
""" 
def organize_weather_data(noaa_key, longitude, latitude):
    
    observation_stations = fetch_noaa_data(noaa_key,latitude, longitude, 'observationStations')
    nearest_station = observation_stations['features'][0]['properties']['stationIdentifier']
    print(nearest_station)

    url = 'https://api.weather.gov/stations/KMTC/observations/latest?require_qc=false'
    response = requests.get(url)
    live_data = response.json().get('properties')
    
    data =  {
       'tempurature': live_data.get('temperature', {}).get('value'),
       'feel_temp' : live_data.get('windChill', {}).get('value'),
       'humidity': live_data.get('relativeHumidity', {}).get('value'),
       'dew_point' : live_data.get('dewpoint', {}).get('value'),
       #'air_pressure' : current.get('pressure_mb'),
       #'visibility' = current.get('vis_miles')
       #'cloud_cover' = current.get('cloud')
       'wind_speed' : live_data.get('windSpeed', {}).get('value'),
       'wind_dir' : live_data.get('windDirection', {}).get('value'),
       'wind_gust' : live_data.get('windGust', {}).get('value'),
       'precipitation last 6 hours' : live_data.get('precipitationLast6Hours', {}).get('value'),
       }
    return data


"""
====================================================================
==========================RANDOM_COORDINATES===========================
INPUTS: NONE
OUTPUTS: LONG/LATITUDE IN MICHIGAIN
====================================================================
DESCRIPTION: THIS FUNCTION GENERATES RANDOM GPS COORDINATES IN THE 
STATE OF MICHIGAN.
====================================================================
====================================================================
""" 
def random_coordinates():
    # Latitude range: 41.7° to 48.3°
    latitude = random.uniform(41.70000000, 48.30000000)
    
    # Longitude range: -90.4° to -82.4°
    longitude = random.uniform(-90.40000000, -82.40000000)
    
    return latitude, longitude


"""
=========================================================================================
========================================MAIN PROGRAM=====================================
=========================================================================================
"""

#latitude, longitude = random_coordinates()
latitude, longitude = 42.37179163178812, -83.47052266145987
noaa_key = 'SpxbLHtRHUnkATNVgVWLLYukjUBEUDDs'
#SpxbLHtRHUnkATNVgVWLLYukjUBEUDDs
api_key = 'ea75d6ac09944795b93162537241401'

forecast_data = fetch_noaa_data(noaa_key,latitude, longitude)

weather_data = organize_weather_data(noaa_key, longitude, latitude)


"""
===============================================
=======CONNECTION TO OUR REALTIME DATABASE=====
===============================================
"""
def post_data(weather_data, latitude, longitude):
# Check if Firebase has already been initialized
    if not firebase_admin._apps:
    # Path to your downloaded service account key
        cred = credentials.Certificate("C:/Users/mjwwr/OneDrive/Documents/Python Scripts/FireBase/ice-spy-firebase-adminsdk-w5zit-79445d7438.json")

    # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ice-spy-default-rtdb.firebaseio.com/'  # Your database URL
    })

# Your code to add data goes here
    ref = db.reference('/ice-reports')  # Reference to your database

#GET CURRENT TIME
    current_time = datetime.now()

    print("Current Time:", current_time)


    ice_report = {
        'report1': {
            'location': {
                'latitude': latitude,
                'longitude': longitude
                },
            'weather': weather_data,
            }
        }
    n = 1
#Was there Ice to detect
    report_data = {
        'timestamp': f'{current_time}',  # Example timestamp
        'location': {},  # Empty initially, to be updated
        'weather': {},   # Empty initially, to be updated
        'ice_detected': None
        }
    if ice_report == None:
        #call gps module to receive lat/long
    
        report_data = {
    'timestamp': f'{current_time}',  
    'location': {
        'latitude': latitude,
        'longitude': longitude
        },
        'weather' : {
            ice_report[f'report{n}']['weather']
        },
     
    'ice_detected': False 
    
        }
    else:    
        for reports in ice_report:
    
            report_data['location'] = ice_report[f'report{n}']['location']
            report_data['weather'] = ice_report[f'report{n}']['weather']
    

    #Increment count 
        n = n+1
        # Push the data to the database
        ref.push(report_data)

    print("Data added successfully!")
post_data(weather_data, latitude, longitude)