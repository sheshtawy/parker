from fastapi import FastAPI
from typing import List

from models import VehicleEntryList
from search import SearchResult, SearchService
from repository import Repository

app = FastAPI(title="Neighbor API")

@app.post("/")
async def root(vehicles: VehicleEntryList) -> List[dict]:
    searchService = SearchService(Repository())
    results: List[SearchResult] = await searchService.search(vehicles)
    return [result.model_dump() for result in results]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)