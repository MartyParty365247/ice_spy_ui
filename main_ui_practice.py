"""
Ice Spy Alert UI

Author: Martin Wrobel
"""
import staticMap
import getData
import lat_math

#Global Var
ref_path = '/ice-reports'
lat = []
long = []
user_lat = 0.0
user_long = 0.0
report_lat = []
report_long = []
#Get Data from database
raw_data = getData.get_firebase_data(ref_path)

#only recveive coordinates form the last x hours
lat, long = getData.extract_recent_lat_lon(raw_data, 120)

#post ALL reports on a single static map
#staticMap.get_static_map(lat, long)

#Simulate getting user loc
user_lat, user_long = staticMap.get_user_loc(48047, "MI")

#Find reports within x number of miles from user
report_lat, report_long = lat_math.find_close_coordinates(raw_data, user_lat, user_long, 20)
print(lat)
print(long)

