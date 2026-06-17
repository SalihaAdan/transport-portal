import streamlit as st
import datetime
from src.data.store import save_poll, get_polls

ROUTES = {
    "Wah Cantt": ["WC1", "WC2", "WC3", "WC4"],
    "G Sector": ["G9", "G10", "G11", "G13"],
    "H Sector": ["H8", "H9", "H11", "H13"],
    "I Sector": ["I8", "I9", "I10", "I11"]
}

UNIVERSITIES = ["FAST NUCES", "NUST", "AIR University", "Bahria University"]

FLEETS = [
  {"id": "Fleet 1", "direction": "Arrival", "base_time": "7:00 AM"},
  {"id": "Fleet 2", "direction": "Arrival", "base_time": "8:00 AM"},
  {"id": "Fleet 3", "direction": "Arrival", "base_time": "9:00 AM"},
  {"id": "Fleet 4", "direction": "Departure", "base_time": "12:00 PM"},
  {"id": "Fleet 5", "direction": "Departure", "base_time": "2:00 PM"},
  {"id": "Fleet 6", "direction": "Arrival", "base_time": "4:00 PM"},
  {"id": "Fleet 7", "direction": "Departure", "base_time": "6:00 PM"},
  {"id": "Fleet 8", "direction": "Departure", "base_time": "8:00 PM"}
]

def add_minutes(time_str, minutes):
    time_obj = datetime.datetime.strptime(time_str, '%I:%M %p')
    new_time = time_obj + datetime.timedelta(minutes=minutes)
    return new_time.strftime('%I:%M %p').lstrip('0')

def show_poll_form():
    st.header("Student Transport Poll")
    st.info("Note: Poll closes 30 minutes before each fleet departs")
    
    try:
        polls = get_polls()
        total_count = len(polls)
    except Exception:
        total_count = 0
        
    st.write(f"**Current total submissions so far:** {total_count}")
    
    route = st.selectbox("Step 1: Select Route", list(ROUTES.keys()))
    
    stops = ROUTES[route]
    stop = st.selectbox("Step 2: Select Stop", stops)
    
    direction = st.radio("Step 3: Select Direction", ["Arrival", "Departure"])
    
    university = st.selectbox("Step 4: Select University", UNIVERSITIES)
    
    matching_fleets = [f for f in FLEETS if f["direction"] == direction]
    
    stop_index = stops.index(stop) if stop in stops else 0
    minutes_to_add = stop_index * 10
    
    fleet_options = {}
    for f in matching_fleets:
        pickup_time = add_minutes(f["base_time"], minutes_to_add)
        display_str = f'{f["id"]} — Your pickup: {pickup_time}'
        fleet_options[display_str] = f["id"]
        
    selected_fleet_display = st.selectbox("Step 5: Select Fleet", list(fleet_options.keys()))
    
    if st.button("Submit Vote"):
        selected_fleet = fleet_options[selected_fleet_display]
        try:
            save_poll(route, stop, direction, university, selected_fleet)
            st.success("Your vote has been submitted!")
            try:
                new_count = len(get_polls())
                st.success(f"Current total submissions: {new_count}")
            except Exception:
                pass
        except Exception as e:
            st.error(f"Error submitting vote: {e}")