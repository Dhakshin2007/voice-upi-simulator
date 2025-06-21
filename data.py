# data.py

# In a real application, this would come from a database or an API.
MERCHANTS = [
    {"id": "m_01", "name": "Rakesh Sharma Petrol Bunk", "beacon_id": "BEACON_001", "location": "MG Road", "upi_id": "rakesh@upi"},
    {"id": "m_02", "name": "Rakesh Sharma Fuel Stop", "beacon_id": "BEACON_002", "location": "Main Street", "upi_id": "rakeshfuel@upi"},
    {"id": "m_03", "name": "KFC Restaurant & Drive-Thru", "beacon_id": "BEACON_003", "location": "City Center", "upi_id": "kfc@upi"},
    {"id": "m_04", "name": "Starbucks Coffee", "beacon_id": "BEACON_004", "location": "Galleria Mall", "upi_id": "starbucks@upi"},
    {"id": "m_05", "name": "Sharma Electronics", "beacon_id": "BEACON_005", "location": "MG Road", "upi_id": "sharmaelec@upi"},
]

def get_simulated_nearby_beacons():
    """Simulates scanning for nearby BLE beacons."""
    # In a real app, this function would interact with the device's
    # hardware to get a live list of beacons.
    return ["BEACON_001", "BEACON_002", "BEACON_005"]