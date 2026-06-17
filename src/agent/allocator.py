import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

from src.data.store import (
    get_polls_grouped,
    save_allocation,
    get_allocations,
    get_polls
)

# Predefined route stops
ROUTE_STOPS = {
    "Wah Cantt": ["WC1", "WC2", "WC3", "WC4"],
    "G Sector": ["G9", "G10", "G11", "G13"],
    "H Sector": ["H8", "H9", "H11", "H13"],
    "I Sector": ["I8", "I9", "I10", "I11"]
}

# Predefined fleet base times
FLEET_BASE_TIMES = {
    "Fleet 1": "7:00 AM",
    "Fleet 2": "8:00 AM",
    "Fleet 3": "9:00 AM",
    "Fleet 4": "12:00 PM",
    "Fleet 5": "2:00 PM",
    "Fleet 6": "4:00 PM",
    "Fleet 7": "6:00 PM",
    "Fleet 8": "8:00 PM"
}

# Predefined university order for departure fleets
UNIVERSITY_ORDER = ["Bahria", "FAST", "AIR", "NUST"]

def run_allocation():
    """
    Reads all grouped polls, calls Gemini API to allocate vehicles,
    parses response, saves allocations, and returns them.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")
    
    # Get and validate grouped polls
    grouped_polls = get_polls_grouped()
    if not grouped_polls:
        raise ValueError("No poll data available for allocation.")
    
    # Convert tuple keys to a list of dicts for JSON serialization in the prompt
    serializable_polls = []
    for (route, fleet), details in grouped_polls.items():
        serializable_polls.append({
            "route": route,
            "fleet": fleet,
            "direction": details["direction"],
            "total_students": details["total_students"],
            "universities": details["universities"]
        })
        
    # Configure Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Build prompt
    prompt = f"""
You are the AI Allocation Agent for a university bus system.
Your job is to decide which vehicles to allocate per route per fleet based on student poll submissions.

Grouped Poll Data:
{json.dumps(serializable_polls, indent=2)}

Fleet Vehicle Inventory:
- 4 Buses (40 seats each)
- 4 Coasters (24 seats each)
- 4 Minis (15 seats each)

Allocation Rules:
- <= 5 students -> 1 Taxi
- 6-15 students -> 1 Mini
- 16-24 students -> 1 Coaster
- 25-40 students -> 1 Bus
- 41-55 students -> 1 Bus + 1 Mini
- 56-64 students -> 1 Bus + 1 Coaster
- 65-80 students -> 2 Buses
- For higher numbers, calculate the best combination using the capacities (Bus: 40, Coaster: 24, Mini: 15).
- Multiple vehicles on the same route travel as a convoy.

Response Instructions:
- Return ONLY a raw JSON array.
- Do NOT wrap the response in markdown code blocks (such as ```json ... ```).
- Do NOT include any introductory or concluding text.
- Each item in the JSON array must be an object containing exactly these keys:
  - route (string)
  - fleet (string)
  - direction (string)
  - total_students (integer)
  - vehicles_assigned (string, e.g. "1 Mini", "1 Bus + 1 Coaster")
  - reasoning (string, exactly one sentence explaining the vehicle selection based on student seat count)
"""
    
    # Call Gemini API
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Programmatically clean any markdown code block wrapper if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()
    
    try:
        allocations = json.loads(response_text)
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}\nRaw Response: {response_text}")
        
    saved_allocations = []
    # Save each allocation and print logs
    for item in allocations:
        route = item["route"]
        fleet = item["fleet"]
        direction = item["direction"]
        total_students = int(item["total_students"])
        vehicles_assigned = item["vehicles_assigned"]
        reasoning = item["reasoning"]
        
        save_allocation(
            route=route,
            fleet=fleet,
            direction=direction,
            total_students=total_students,
            vehicles_assigned=vehicles_assigned,
            reasoning=reasoning
        )
        print(f"[DECISION] Route: {route} | Fleet: {fleet} | Direction: {direction} | Students: {total_students} | Vehicles: {vehicles_assigned} | Reasoning: {reasoning}")
        saved_allocations.append(item)
        
    return saved_allocations

def get_student_allocation(route, fleet, stop, direction):
    """
    Reads allocations.csv and returns the assigned vehicles and exact pickup/drop-off
    time for the specific stop+fleet combination.
    """
    allocations = get_allocations()
    
    # Find matching allocation
    matching_alloc = None
    target_fleet_str = str(fleet).strip().lower()
    # Normalize comparison fleet string
    if not target_fleet_str.startswith("fleet"):
        target_fleet_str = f"fleet {target_fleet_str}"
        
    for alloc in allocations:
        alloc_route = alloc["route"].strip().lower()
        alloc_fleet = alloc["fleet"].strip().lower()
        alloc_dir = alloc["direction"].strip().lower()
        
        if not alloc_fleet.startswith("fleet"):
            alloc_fleet = f"fleet {alloc_fleet}"
            
        if (alloc_route == route.strip().lower() and 
            alloc_fleet == target_fleet_str and 
            alloc_dir == direction.strip().lower()):
            matching_alloc = alloc
            break
            
    if not matching_alloc:
        return None
        
    # Get base time for the fleet
    fleet_name = str(fleet).strip()
    if not fleet_name.lower().startswith("fleet"):
        fleet_name = f"Fleet {fleet_name}"
    base_time_str = FLEET_BASE_TIMES.get(fleet_name)
    if not base_time_str:
        raise ValueError(f"Unknown fleet or base time for {fleet}")
        
    # Find stop index
    stops = ROUTE_STOPS.get(route)
    if not stops:
        raise ValueError(f"Unknown route: {route}")
    if stop not in stops:
        raise ValueError(f"Unknown stop {stop} for route {route}")
    stop_index = stops.index(stop)
    
    # Calculate offset in minutes
    if direction.strip().lower() == "arrival":
        minutes_offset = stop_index * 10
    elif direction.strip().lower() == "departure":
        # Look up university of the student at that stop in polls.csv
        polls = get_polls()
        univ_name = "FAST" # Default fallback
        for p in polls:
            p_route = p.get("route", "").strip().lower()
            p_fleet = p.get("fleet", "").strip().lower()
            p_stop = p.get("stop", "").strip().lower()
            p_dir = p.get("direction", "").strip().lower()
            
            p_fleet_norm = p_fleet if p_fleet.startswith("fleet") else f"fleet {p_fleet}"
            
            if (p_route == route.strip().lower() and 
                p_fleet_norm == target_fleet_str and 
                p_stop == stop.strip().lower() and 
                p_dir == direction.strip().lower()):
                univ_name = p.get("university", "FAST").strip()
                break
                
        # Find university order index
        univ_index = 0
        univ_upper = univ_name.upper()
        for idx, u in enumerate(UNIVERSITY_ORDER):
            if u in univ_upper:
                univ_index = idx
                break
                
        # Reverse stop index calculation
        reverse_stop_index = len(stops) - 1 - stop_index
        minutes_offset = (univ_index * 10) + (reverse_stop_index * 10)
    else:
        raise ValueError(f"Invalid direction: {direction}")
        
    # Calculate exact pickup time
    base_time_dt = datetime.strptime(base_time_str.strip(), "%I:%M %p")
    pickup_time_dt = base_time_dt + timedelta(minutes=minutes_offset)
    pickup_time = pickup_time_dt.strftime("%I:%M %p").lstrip("0")
    
    return {
        "vehicles_assigned": matching_alloc["vehicles_assigned"],
        "pickup_time": pickup_time
    }
