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
    
    
ref_path = '/ice-reports'

raw_data = get_firebase_data(ref_path)
print(raw_data)
