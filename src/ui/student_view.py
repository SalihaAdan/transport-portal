import streamlit as st
from src.ui.poll_form import ROUTES, FLEETS, add_minutes
from src.agent.allocator import get_student_allocation

def show_student_view():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-family: Outfit, sans-serif;'>Check My Bus 🚌</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4B5563; font-family: Inter, sans-serif;'>Find out which bus is assigned to your stop</p>", unsafe_allow_html=True)
    
    # Simple form container styling
    st.markdown(
        """
        <div style='background-color: #F3F4F6; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto;'>
        """,
        unsafe_allow_html=True
    )
    
    # Route Selection
    routes_list = list(ROUTES.keys())
    route = st.selectbox("Select your route", routes_list, key="student_route")
    
    # Stop Selection (dynamic based on route)
    stops_list = ROUTES[route]
    stop = st.selectbox("Select your stop", stops_list, key="student_stop")
    
    # Direction Selection
    direction = st.selectbox("Select your direction (Arrival/Departure)", ["Arrival", "Departure"], key="student_direction")
    
    # Fleet Selection (filtered by direction, shows exact pickup time)
    stop_index = ROUTES[route].index(stop) if stop in ROUTES[route] else 0
    minutes_to_add = stop_index * 10

    fleet_options = []
    for f in FLEETS:
        if f["direction"] == direction:
            pickup_time = add_minutes(f["base_time"], minutes_to_add)
            fleet_options.append(f"{f['id']} [Pickup time: {pickup_time}]")
        
    fleet = st.selectbox("Select your fleet", fleet_options, key="student_fleet")
    
    find_btn = st.button("Find My Bus", use_container_width=True, type="primary")
    
    if find_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        # Call allocation getter
        # The fleet parameter will look like "Fleet 1 (Early Morning) [Pickup time: 07:10]"
        # get_student_allocation will strip the bracket part
        fleet_raw = fleet.split(" [")[0]
        alloc = get_student_allocation(route, fleet_raw, stop, direction)
        
        if alloc:
            st.success(
                f"""
                **Your bus:** {alloc['vehicles_assigned']}  
                **Pickup time at your stop:** {alloc['pickup_time']}  
                **Direction:** {direction}
                """
            )
        else:
            st.warning("Allocation not published yet. Check back after poll closes.")
            
    st.markdown("</div>", unsafe_allow_html=True)