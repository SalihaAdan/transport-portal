import streamlit as st
from src.data.store import get_polls, get_allocations, clear_polls, clear_allocations
from src.agent.allocator import run_allocation

def show_dashboard():
    # Title
    st.markdown("<h1 style='color: #1E3A8A; font-family: Outfit, sans-serif;'>Transport Office Dashboard 📊</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0; margin-bottom: 25px;'>", unsafe_allow_html=True)
    
    # Retrieve current polls
    polls_df = get_polls()
    total_polls = len(polls_df)
    
    # Top Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(
            f"""
            <div style='background-color: #EFF6FF; border-left: 5px solid #3B82F6; padding: 15px; border-radius: 5px;'>
                <p style='margin: 0; font-size: 14px; color: #1E40AF; font-weight: bold;'>Total Poll Submissions</p>
                <h2 style='margin: 5px 0 0 0; color: #1E3A8A;'>{total_polls}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        allocate_btn = st.button("Close Poll & Allocate Buses", use_container_width=True, type="primary")
        
    # Trigger allocation on button click
    if allocate_btn:
        try:
            with st.spinner("Agent is analyzing poll data..."):
                run_allocation()
            st.success("Allocation complete!")
            st.balloons()
        except Exception as e:
            st.error(f"Allocation Failed: {str(e)}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["Poll Results", "Bus Allocations"])
    
    with tab1:
        st.markdown("<h4 style='color: #1E3A8A; font-family: Outfit, sans-serif;'>Poll Results Summary</h4>", unsafe_allow_html=True)
        if not polls_df:
            st.markdown("<p style='color: #6B7280; font-style: italic;'>No submissions yet</p>", unsafe_allow_html=True)
        else:
            from collections import defaultdict
            grouped = defaultdict(int)
            for p in polls_df:
                grouped[(p["route"], p["fleet"])] += 1
            table_data = [{"Route": r, "Fleet": f, "Student Count": c} for (r, f), c in grouped.items()]
            st.dataframe(table_data, use_container_width=True, hide_index=True)
            
    with tab2:
        st.markdown("<h4 style='color: #1E3A8A; font-family: Outfit, sans-serif;'>Allocated Fleets</h4>", unsafe_allow_html=True)
        allocations = get_allocations()
        
        if not allocations:
            st.markdown("<p style='color: #6B7280; font-style: italic;'>Run allocation first</p>", unsafe_allow_html=True)
        else:
            for idx, alloc in enumerate(allocations):
                route_name = alloc.get("route", "")
                fleet_name = alloc.get("fleet", "")
                direction = alloc.get("direction", "")
                students_count = alloc.get("total_students", 0)
                vehicles_assigned = alloc.get("vehicles_assigned", "No vehicles assigned")
                reasoning = alloc.get("reasoning", "")
                
                # Fetch base time for display
                base_time = "See fleet schedule"
                
                # Card Container
                with st.container(border=True):
                    st.markdown(f"<h4 style='margin: 0; color: #1E3A8A; font-family: Outfit, sans-serif;'>{route_name}</h4>", unsafe_allow_html=True)
                    st.write(f"**Schedule:** {fleet_name} | **Direction:** {direction} | **Base Time:** {base_time}")
                    st.write(f"**Total Students:** {students_count}")
                    st.success(f"Vehicles assigned: {vehicles_assigned}")
                    st.markdown(f"*Agent reasoning: {reasoning}*")
                    
    st.markdown("<br><hr style='border-top: 1px solid #E5E7EB;'><br>", unsafe_allow_html=True)
    
    # Reset Button
    reset_btn = st.button("Reset Everything", use_container_width=True)
    if reset_btn:
        clear_polls()
        clear_allocations()
        st.success("Successfully reset all data!")
        st.rerun()