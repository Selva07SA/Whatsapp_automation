SLOTS = {
    "1": "6-7 AM",
    "2": "7-8 AM",
    "3": "8-9 AM",
    "4": "9-10 AM",
    "5": "10-11 AM",
    "6": "11-12 PM",
    "7": "12-1 PM",
    "8": "1-2 PM",
    "9": "2-3 PM",
    "10": "3-4 PM"
}

def get_available_slots(booked_slots):
    return {k: v for k, v in SLOTS.items() if v not in booked_slots}
