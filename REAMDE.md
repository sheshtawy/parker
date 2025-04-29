# Multi-Vehicle Search API

A FastAPI-based service that helps renters find storage locations for multiple vehicles. The service implements an efficient bin packing algorithm to find optimal storage solutions.

## Overview

The service provides an API endpoint that accepts a list of vehicles with their dimensions and quantities, then returns possible storage locations sorted by total price. The algorithm ensures the most cost-effective storage solution for all vehicles while respecting space constraints.

**Github Repo** - https://github.com/sheshtawy/parker

**Link to API** - [parker.sheshtawy.dev](parker.sheshtawy.dev)

## Technical Stack

- Python 3.9+
- FastAPI - Web framework
- Pydantic - Data validation
- pytest - Testing

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service locally

Start the server:
```bash
python server.py
```

The server will start at `http://0.0.0.0:8000`

## Deployment

This service is deployed to [Render](https://render.com/). You can find it at [`parker.sheshtawy.dev`](parker.sheshtawy.dev) or the original instance URL [`https://parker-s5ih.onrender.com/`](https://parker-s5ih.onrender.com/) if for some reason the DNS resolution isn't working.

### Assumptions

1. All vehicles at a listing are stored in the same orientation
2. No buffer space is required between vehicles
3. Vehicle width is fixed at 10 feet
4. All listing dimensions are multiples of 10
5. Maximum of 5 total vehicles per request

## Testing

### Integration and Unit Tests
Run the test suite:
```bash
pytest
```

The test suite includes:
- Unit tests for the search algorithm
- Integration tests for the API endpoint
- Test cases for various vehicle combinations

### API Manual Testing
Below is a working example request

```bash
curl --location 'parker.sheshtawy.dev' \
--header 'Content-Type: application/json' \
--data '[
    {
        "length": 50,
        "quantity": 2
    },
    {
        "length": 40,
        "quantity": 1
    },
    {
        "length": 50,
        "quantity": 2
    }
]'
```

## Implementation Details

### Architecture

- `server.py` - FastAPI application and endpoint definitions
- `models.py` - Data models and validation
- `search.py` - Core search algorithm implementation
- `repository.py` - Data access layer using in-memory storage
- `constants.py` - Shared constants

### Search Algorithm

The service implements a variant of the First Fit Decreasing (FFD) bin packing algorithm with the following optimizations:

1. Grid-based space allocation algrithm does the following:
    - Sorts vehicles by length in descending order
    - Sorts listings by total area in descending order
    - Creates a grid system for each listing where:
        - Each cell is 10ft x 10ft
        - Columns are based on shorter listing dimension
        - Rows are based on longer listing dimension
    - Places vehicles in available grid spaces using first-fit approach. The grid system ensures efficient space utilization by lining up vehicles in rows while maintaining the lowest possible cost per location.

2. Pre-filtering:
   - Locations are pre-filtered based on total available space
   - Only viable locations are processed by the FFD algorithm

3. Cost optimization:
   - Results are sorted by total price
   - Each location returns the most cost-effective combination of listings

## Data Storage

I restructed the data into `listings_by_location.json` grouping listings by location to simplify the search implementation. This way, we avoid the duplicative work of filtering listings by location every time we need to peform a search query