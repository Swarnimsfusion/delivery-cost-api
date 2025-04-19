from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import math
from itertools import permutations
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware for frontend/API testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint (Render health check)
@app.get("/")
def read_root():
    return {"message": "App is live!"}

# Product-center and weight mappings
PRODUCT_CENTER = {
    "A": "C1", "B": "C1", "C": "C1",
    "D": "C2", "E": "C2", "F": "C2",
    "G": "C3", "H": "C3", "I": "C3"
}

PRODUCT_WEIGHT = {
    "A": 3, "B": 2, "C": 8,
    "D": 12, "E": 25, "F": 15,
    "G": 0.5, "H": 1, "I": 2
}

DIST = {
    "C1": {"L1": 3, "C2": 4, "C3": 3},
    "C2": {"L1": 2, "C1": 4, "C3": 2.5},
    "C3": {"L1": 2, "C1": 3, "C2": 2.5},
    "L1": {"C1": 3, "C2": 2, "C3": 2}
}

# Input model for API
class Order(BaseModel):
    A: int = 0
    B: int = 0
    C: int = 0
    D: int = 0
    E: int = 0
    F: int = 0
    G: int = 0
    H: int = 0
    I: int = 0

# Cost per weight slab
def slab_rate(w: float) -> float:
    if w <= 5:
        return 10
    extra = w - 5
    slabs = math.ceil(extra / 5)
    return 10 + slabs * 8

# Main delivery cost API
@app.post("/calculate-cost")
def calculate_cost(order: Order):
    data = order.dict()
    center_w: Dict[str, float] = {}

    # Step 1: Group product weights by center
    for p, qty in data.items():
        if qty > 0:
            center = PRODUCT_CENTER[p]
            weight = PRODUCT_WEIGHT[p] * qty
            center_w[center] = center_w.get(center, 0) + weight

    centers = list(center_w.keys())
    best = float("inf")

    # Step 2: Try all permutations of pickup sequences
    for start in centers:
        others = [c for c in centers if c != start]
        for perm in permutations(others):
            cost = 0
            # First delivery from start → L1
            w0 = center_w[start]
            cost += DIST[start]["L1"] * slab_rate(w0)

            # Then pickup → deliver sequences
            for c in perm:
                cost += DIST["L1"][c] * slab_rate(0)         # Empty pickup trip
                cost += DIST[c]["L1"] * slab_rate(center_w[c])  # Deliver back to L1

            best = min(best, cost)

    return {"minimum_cost": round(best)}

# For running locally or on Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
