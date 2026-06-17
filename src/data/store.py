import os
import csv
import datetime

# Setup paths relative to this file's location to ensure portability
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
POLLS_CSV = os.path.join(DATA_DIR, "polls.csv")
ALLOCATIONS_CSV = os.path.join(DATA_DIR, "allocations.csv")

def init_csv_files():
    """Initializes the CSV files with headers if they do not exist or are empty."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize polls.csv
    if not os.path.exists(POLLS_CSV) or os.path.getsize(POLLS_CSV) == 0:
        with open(POLLS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["route", "stop", "direction", "university", "fleet", "timestamp"])
            
    # Initialize allocations.csv
    if not os.path.exists(ALLOCATIONS_CSV) or os.path.getsize(ALLOCATIONS_CSV) == 0:
        with open(ALLOCATIONS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["route", "fleet", "direction", "total_students", "vehicles_assigned", "reasoning", "timestamp"])

# Initialize immediately upon import
init_csv_files()

def save_poll(route, stop, direction, university, fleet):
    """Appends one row to polls.csv with current timestamp."""
    init_csv_files()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(POLLS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([route, stop, direction, university, fleet, timestamp])
    print(f"[LOG] Saved poll: route={route}, stop={stop}, direction={direction}, university={university}, fleet={fleet}, timestamp={timestamp}")

def get_polls():
    """Returns all rows from polls.csv as a list of dicts."""
    init_csv_files()
    polls = []
    with open(POLLS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            polls.append(dict(row))
    return polls

def get_polls_grouped():
    """
    Returns a dict grouped by route+fleet combination.
    Each group contains total student count and breakdown by university.
    
    Structure of returned dict:
    {
        (route, fleet): {
            "total_students": int,
            "direction": str,
            "universities": {
                "University Name": count,
                ...
            }
        }
    }
    """
    polls = get_polls()
    grouped = {}
    for poll in polls:
        route = poll["route"]
        fleet = poll["fleet"]
        direction = poll["direction"]
        university = poll["university"]
        
        key = (route, fleet)
        if key not in grouped:
            grouped[key] = {
                "total_students": 0,
                "direction": direction,
                "universities": {}
            }
        
        grouped[key]["total_students"] += 1
        grouped[key]["universities"][university] = grouped[key]["universities"].get(university, 0) + 1
        
    return grouped

def clear_polls():
    """Clears all poll data (for demo reset)."""
    with open(POLLS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["route", "stop", "direction", "university", "fleet", "timestamp"])
    print("[LOG] Cleared all poll data.")

def save_allocation(route, fleet, direction, total_students, vehicles_assigned, reasoning):
    """Appends one row to allocations.csv with current timestamp."""
    init_csv_files()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALLOCATIONS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([route, fleet, direction, total_students, vehicles_assigned, reasoning, timestamp])
    print(f"[LOG] Saved allocation: route={route}, fleet={fleet}, direction={direction}, total_students={total_students}, vehicles_assigned={vehicles_assigned}, timestamp={timestamp}")

def get_allocations():
    """Returns all rows from allocations.csv as a list of dicts."""
    init_csv_files()
    allocations = []
    with open(ALLOCATIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            allocations.append(dict(row))
    return allocations

def clear_allocations():
    """Clears all allocation data."""
    with open(ALLOCATIONS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["route", "fleet", "direction", "total_students", "vehicles_assigned", "reasoning", "timestamp"])
    print("[LOG] Cleared all allocation data.")
