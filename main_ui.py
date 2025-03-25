"""
Ice Spy Alert UI - Streamlit Web App

Author: Martin Wrobel
"""

import streamlit as st
import staticMap
import getData
import lat_math
from datetime import datetime

# Constants
REF_PATH = '/ice-reports'

# Load Firebase Data
@st.cache_data(ttl=300)  # Refresh every 5 min
def load_data():
    return getData.get_firebase_data(REF_PATH)

# Main Streamlit App
def main():
    st.set_page_config(page_title="Ice Spy Alert", layout="centered")
    col1, col2, col3 = st.columns([1, 2, 1])  # Wider center column
    with col2:
        st.image("logo.png", width=300)
        st.title("Ice Spy Alert")

    # Load Firebase data
    raw_data = load_data()
    print(raw_data)

    st.header("🗺️ All Ice Reports (Past 3 Hours)")
    lat_recent, long_recent = getData.extract_recent_lat_lon(raw_data, hours=24)
    if lat_recent and long_recent:
        staticMap.get_static_map_st(lat_recent, long_recent)
    else:
        st.info("No ice reports in the past 3 hours.")

    st.divider()

    st.header("📍 Find Ice Reports Near You")
    zip_code = st.text_input("Enter your ZIP code:", max_chars=5)
    state = st.text_input("Enter your 2-letter state abbreviation:")

    if st.button("Check Ice Reports Nearby"):
        if not zip_code or not state:
            st.warning("Please enter a valid ZIP code and state.")
        else:
            try:
                user_lat, user_long = staticMap.get_user_loc(int(zip_code), state)
                nearby_lat, nearby_long = lat_math.find_recent_close_coordinates(raw_data, user_lat, user_long, hours=24, max_distance=20)

                if nearby_lat and nearby_long:
                    st.success("Displaying ice reports within 20 miles of your location:")
                    staticMap.get_static_map_st(nearby_lat, nearby_long)
                else:
                    st.info("No ice reports found within 20 miles in the last 3 hours.")
            except Exception as e:
                st.error(f"Error retrieving data: {e}")

if __name__ == "__main__":
    main()
