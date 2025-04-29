from typing import Dict, List, Optional
import json
from models import Listing, Location

class Repository:
    def __init__(self):
        # This is a simple in-memory storage
        # In a real application, this would be replaced with a database
        self._storage: Dict = {}
        self._load_from_file()
    
    def get(self, key: str) -> Optional[dict]:
        return self._storage.get(key)
    
    def get_all(self) -> List[Location]:
        return list(self._storage.values())
    
    def _load_from_file(self) -> None:
        try:
            with open('listings_by_location.json', 'r') as f:
                data = json.load(f)
                for location_id, listings in data.items():
                    location = Location(id=location_id)
                    for listing_data in listings:
                        if isinstance(listing_data, dict) and 'id' in listing_data:  # Skip incomplete entries
                            listing = Listing(**listing_data)
                            location.listings.append(listing)
                    self._storage[location_id] = location
        except FileNotFoundError:
            print("Warning: listings_by_location.json not found")
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in listings_by_location.json")