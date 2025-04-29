import pytest
from models import Listing, Location, VehicleEntryList
from search import SearchService
from repository import Repository

class MockRepository:
    def __init__(self, locations):
        self.locations = locations

    def get_all(self):
        return self.locations

@pytest.fixture
def mock_locations():
    location1 = Location(id="loc1")
    location1.listings = [
        Listing(id="l1", width=20, length=30, price_in_cents=5000),
        Listing(id="l2", width=40, length=50, price_in_cents=10000)
    ]
    
    location2 = Location(id="loc2")
    location2.listings = [
        Listing(id="l3", width=10, length=20, price_in_cents=3000)
    ]
    
    return [location1, location2]

@pytest.fixture
def search_service(mock_locations):
    repo = MockRepository(mock_locations)
    return SearchService(repo)

@pytest.mark.asyncio
async def test_search_single_vehicle(search_service):
    vehicles = VehicleEntryList.model_validate([
        {"length": 20, "quantity": 1}
    ])
    
    results = await search_service.search(vehicles)
    assert len(results) == 2
    assert results[0].location_id == "loc2"
    assert len(results[0].listing_ids) == 1

@pytest.mark.asyncio
async def test_search_multiple_vehicles(search_service):
    vehicles = VehicleEntryList.model_validate([
        {"length": 20, "quantity": 2},
        {"length": 30, "quantity": 1}
    ])
    
    results = await search_service.search(vehicles)
    assert len(results) > 0
    # Results should be sorted by price
    for i in range(1, len(results)):
        assert results[i].total_price_in_cents >= results[i-1].total_price_in_cents
