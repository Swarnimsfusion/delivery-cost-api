from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from itertools import permutations
import math
import os

app = FastAPI(
    title="Delivery Cost API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check
@app.get("/")
def read_root():
    return {"message": "App is live!"}

# ✅ Product weights
product_weight = {
    "A": 3, "B": 2, "C": 8,
    "D": 12, "E": 25, "F": 15,
    "G": 0.5, "H": 1, "I": 2
}

# ✅ Product-center mapping
product_center = {
    "A": "C1", "B": "C1", "C": "C1",
    "D": "C2", "E": "C2", "F": "C2",
    "G": "C3", "H": "C3", "I": "C3"
}

# ✅ Distances
dist = {
    "C1": {"L1": 3, "C2": 4, "C3": 3},
    "C2": {"L1": 2, "C1": 4, "C3": 3},
    "C3": {"L1": 2, "C1": 3, "C2": 3},
    "L1": {"C1": 3, "C2": 2, "C3": 2}
}

# ✅ Slab rate logic
def slab_rate(weight):
    if weight <= 5:
        return 10
    extra = weight - 5
    slabs = math.ceil(extra / 5)
    return 10 + slabs * 8

# ✅ Request model
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

# ✅ Cost calculation route
@app.post("/calculate-cost")
def calculate_cost(order: Order):
    data = order.dict()

    # Calculate total weight per center
    center_weights: Dict[str, float] = {}
    for p, qty in data.items():
        if qty > 0:
            c = product_center[p]
            w = product_weight[p] * qty
            center_weights[c] = center_weights.get(c, 0) + w

    centers = list(center_weights.keys())
    best_cost = float("inf")

    for start in centers:
        others = [c for c in centers if c != start]
        for route in permutations(others):
            total_cost = 0
            # First trip: start → L1
            w1 = center_weights[start]
            total_cost += dist[start]["L1"] * slab_rate(w1)

            # Remaining trips: L1 → other_center → L1
            for c in route:
                total_cost += dist["L1"][c] * slab_rate(0)  # empty trip
                total_cost += dist[c]["L1"] * slab_rate(center_weights[c])  # loaded trip

            best_cost = min(best_cost, total_cost)

    return {"minimum_cost": round(best_cost)}

# ✅ For local dev or Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
