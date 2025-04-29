import math
from dataclasses import dataclass
from typing import List, Set

from pydantic import BaseModel
from constants import DEFAULT_VEHICLE_WIDTH
from models import Location, VehicleEntryList
from repository import Repository
from models import SearchResult

class SearchService:
    def __init__(self, repository: Repository):
        self.repository = repository
    
    async def search(self, vehicles: VehicleEntryList) -> List[SearchResult]:
        """
        Placeholder for future search implementation.
        This will contain the business logic for searching through the data.
        """
        listings_by_location = self.repository.get_all()
        # Run a quick check to filter out locations that we are confident won't fit any of our
        filtered_locations = [location for location in listings_by_location if self._can_fit_vehicles_in_location(vehicles, location)]
        
        results = sorted(
            [self.ffd(location, vehicles) for location in filtered_locations],
            key=lambda result: result.total_price_in_cents
        )
            
        return results

        # Iterate through each vehicle and find the best matching listings

    def ffd(self, location: Location, vehicles: VehicleEntryList) -> SearchResult:
        """
        First Fit Decreasing algorithm to find the best matching listings for a vehicle.
        This implementation uses a grid-based approach to efficiently place vehicles in available listings.
        The algorithm sorts vehicles by length in descending order and listings by total area to maximize space utilization.
        Args:
            location (Location): Location object containing available listings
            vehicles (VehicleEntryList): List of vehicles to be stored, containing length and quantity info
        Returns:
            SearchResult: Object containing:
                - location_id: ID of the location
                - listing_ids: List of selected listing IDs that can fit all vehicles
                - total_price_in_cents: Total cost of selected listings in cents
        Raises:
            Exception: When unable to fit all vehicles in available listings
        Algorithm Details:
            1. Sorts vehicles by length in descending order
            2. Sorts listings by total area in descending order
            3. Creates a grid system for each listing where:
                - Each cell is 10ft x 10ft
                - Columns are based on shorter listing dimension
                - Rows are based on longer listing dimension
            4. Places vehicles in available grid spaces using first-fit approach
        Note:
            The grid system ensures efficient space utilization by lining up vehicles in rows
            while maintaining the lowest possible cost per location.
        """
        
        # Sort listings by total area to maximize no. of vehicles per listing (i.e. minimize listings) needed
        sorted_listings = sorted(location.listings, key=lambda x: x.area, reverse=True)
        
        # Initialize the selected listings and total price
        selected_listings: Set[str] = set()
        total_price = 0

        # Split listings capacity into a grid of equal sized cells. Each cell is 10 ft x 10 ft
        # This makes placing vehicles in listed spaces efficient. By using the "grid" concept, we can line-up
        # vehicles in rows, maximizing listed space utilization, and ensuring lowest cost possible per location

        listing_grids = []
        remaining_capacity = {}
        for listing in sorted_listings:
             # Flatten and sort vehicles list to have individual entries per vehicle sorted by length
            vehicle_lengths = []
            for vehicle in vehicles.root:
                vehicle_lengths.extend([vehicle.length] * vehicle.quantity)
            vehicle_lengths = sorted(vehicle_lengths, reverse=True)
            # We want the longer side of the space to dictate the depth of each column to make sure the longest vehicle will fit in a column
            rows = max(listing.length, listing.width) // DEFAULT_VEHICLE_WIDTH
            # We want the shorter side of the space to be the number of coumns available
            cols = min(listing.length, listing.width) // DEFAULT_VEHICLE_WIDTH
            remaining_capacity[listing.id] = [rows] * cols  # start with an empty grid
            listing_grids.append((listing.id, cols, rows, listing.price_in_cents))
        


        for vehicle_length in vehicle_lengths:
            vehicle_size = math.ceil(vehicle_length / DEFAULT_VEHICLE_WIDTH)
            stored = False
            stored_count = 0

            for id, cols, rows, price in listing_grids:
                for col_idx in range(cols):
                    if remaining_capacity[id][col_idx] >= vehicle_size:
                        remaining_capacity[id][col_idx] -= vehicle_size
                        if(id not in selected_listings):
                            selected_listings.add(id)
                            total_price += price
                        stored = True
                        stored_count += 1
                        break
                if stored:
                    break

        return SearchResult(location_id=location.id, listing_ids=list(selected_listings), total_price_in_cents=total_price)


    def _can_fit_vehicles_in_location(self, vehicle_entries: VehicleEntryList, location: Location) -> bool:
        """
        Determines whether the given vehicles can fit within the specified location.
        Args:
            vehicle_entries (VehicleEntryList): A list of vehicle entries, where each entry contains 
                details about the vehicle's dimensions and quantity.
            location (Location): A location object containing a list of listings, 
                where each listing specifies its dimensions.
        Returns:
            bool: True if the vehicles can fit within the location based on the area, 
            length, and width constraints; False otherwise.
        Logic:
            - Returns False if:
                - The total area required by all vehicles exceeds the total area 
              available in the location.
                - The largest vehicle cannot fit within the largest listing 
              in the location by either width or length.
                - The total length of all vehicles exceeds the total capacity 
              of the listings in the location when considering both length and width constraints.
            - Returns True otherwise.
        """

        if vehicle_entries.total_area > location.total_area:
            return False
            
        max_vehicle_length = max([vehicle.length for vehicle in vehicle_entries.root])
        max_listing_length = max([listing.length for listing in location.listings])
        max_listing_width = max([listing.width for listing in location.listings])
        if max_vehicle_length > max_listing_length and max_vehicle_length > max_listing_width:
            return False
        
        total_vehicles_length = sum(vehicle.length * vehicle.quantity for vehicle in vehicle_entries.root)
        total_listings_capacity_by_length = sum((listing.width // DEFAULT_VEHICLE_WIDTH) * listing.length for listing in location.listings)
        total_listings_capacity_by_width = sum((listing.length // DEFAULT_VEHICLE_WIDTH) * listing.width for listing in location.listings)
        if total_vehicles_length > total_listings_capacity_by_length and total_vehicles_length > total_listings_capacity_by_width:
            return False

        return True





