from math import radians, cos, sin, sqrt, atan2
from datetime import datetime, timedelta

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in miles."""
    R = 3958.8  # Earth radius in miles

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def find_close_coordinates(data, ref_lat, ref_lon, max_distance=20):
    """Return lat/lon arrays of points within max_distance (miles) of a reference point."""
    nearby_latitudes = []
    nearby_longitudes = []

    for key, entry in data.items():
        location = entry.get("location", {})
        lat = location.get("latitude")
        lon = location.get("longitude")

        if lat is not None and lon is not None:
            distance = haversine_distance(ref_lat, ref_lon, lat, lon)
            if distance <= max_distance:
                nearby_latitudes.append(lat)
                nearby_longitudes.append(lon)

    return nearby_latitudes, nearby_longitudes

def find_recent_close_coordinates(data, ref_lat, ref_lon, hours=5, max_distance=20):
    """Return lat/lon arrays of points within 'hours' and within 'max_distance' (miles) of a given location."""
    now = datetime.now()
    cutoff = now - timedelta(hours=hours)

    nearby_latitudes = []
    nearby_longitudes = []

    for key, entry in data.items():
        timestamp_str = entry.get("timestamp")
        location = entry.get("location", {})

        lat = location.get("latitude")
        lon = location.get("longitude")

        if timestamp_str and lat is not None and lon is not None:
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                if timestamp > cutoff:
                    distance = haversine_distance(ref_lat, ref_lon, lat, lon)
                    if distance <= max_distance:
                        nearby_latitudes.append(lat)
                        nearby_longitudes.append(lon)
            except ValueError:
                print(f"{key}: Invalid timestamp format")

    return nearby_latitudes, nearby_longitudes

