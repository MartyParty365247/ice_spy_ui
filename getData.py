# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 12:09:37 2025

@author: mjwwr
"""

from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # Path to your downloaded service account key
        cred = credentials.Certificate("secrets.toml")

    # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ice-spy-default-rtdb.firebaseio.com/'  # Your database URL
    })

# Function to fetch data from a specific path
def get_firebase_data(reference_path):
    try:
        ref = db.reference(reference_path)  # Get reference to the data
        data = ref.get()  # Retrieve data
        if data:
            print("Data Retrieved Successfully:")
            print(data)
        else:
            print("No data found at the specified reference.")
        return data
    except Exception as e:
        print("Error fetching data:", e)
        return None
    
"""
 ==============================================================
 ========================GET_COORDINATES=======================
 Get Coordinates of every ice report in Data base
 ==============================================================
 """
 
 
def get_coordinates(data):
      for key, entry in data.items():
          location = entry.get("location", {})
          lat = location.get("latitude")
          lon = location.get("longitude")
          if lat is not None and lon is not None:
              print(f"{key}: Latitude = {lat}, Longitude = {lon}")
"""
 ==============================================================
 ===================extract_recent_lat_lon=====================
 Get Coordinates of ice report at specified time
 INPUT: RAW_DATA (JSON), # OF HOURS FROM NOW (INT)
 ==============================================================
"""
def extract_recent_lat_lon(data, hours=5):
     """Extract latitude and longitude pairs from entries within the last 'hours' hours."""
     now = datetime.now()
     cutoff = now - timedelta(hours=hours)
 
     latitudes = []
     longitudes = []
 
     for key, entry in data.items():
         timestamp_str = entry.get("timestamp")
         if timestamp_str:
             try:
                 timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                 if timestamp > cutoff:
                     location = entry.get("location", {})
                     lat = location.get("latitude")
                     lon = location.get("longitude")
                     if lat is not None and lon is not None:
                         latitudes.append(lat)
                         longitudes.append(lon)
             except ValueError:
                 print(f"{key}: Invalid timestamp format")
 
     return latitudes, longitudes
 
 
 #Test Main
 

