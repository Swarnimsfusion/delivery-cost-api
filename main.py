from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel
from typing import Dict
import os

app = FastAPI(
    title="Delivery Cost API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# ✅ CORS middleware to fix fetch error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (safe for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Simple check for homepage
@app.get("/")
def read_root():
    return {"message": "App is live!"}

# ✅ Product weights (kg per unit) as per PDF
product_weight = {
    "A": 3, "B": 2, "C": 8,
    "D": 12, "E": 25, "F": 15,
    "G": 0.5, "H": 1, "I": 2
}

# ✅ Where each product is stocked
product_center = {
    "A": "C1", "B": "C1", "C": "C1",
    "D": "C2", "E": "C2", "F": "C2",
    "G": "C3", "H": "C3", "I": "C3"
}

# ✅ Distance from centers to L1 and to each other
distances = {
    ("C1", "L1"): 3, ("C2", "L1"): 2, ("C3", "L1"): 2,
    ("C1", "C2"): 4, ("C2", "C1"): 4,
    ("C1", "C3"): 3, ("C3", "C1"): 3,
    ("C2", "C3"): 3, ("C3", "C2"): 3
}

# ✅ Cost per slab
def calculate_slab_cost(weight, distance):
    if weight <= 5:
        return 10 * distance
    remaining = weight - 5
    slabs = (remaining + 4) // 5  # ceil logic
    return 10 * distance + slabs * 8 * distance

# ✅ Order schema (for Pydantic v2)
class OrderRequest(RootModel):
    root: Dict[str, int]

# ✅ Main cost calculator
@app.post("/calculate-cost")
def calculate_cost(order: OrderRequest):
    order_data = order.root

    # Total weight from each center
    center_weights = {"C1": 0, "C2": 0, "C3": 0}
    for item, qty in order_data.items():
        if qty <= 0: continue
        weight = product_weight.get(item, 0)
        center = product_center.get(item)
        if center:
            center_weights[center] += weight * qty

    total_cost = 0
    for center, weight in center_weights.items():
        if weight > 0:
            dist = distances.get((center, "L1"), 0)
            total_cost += calculate_slab_cost(weight, dist)

    return {"minimum_cost": round(total_cost)}

# ✅ Local run support (for Render compatibility)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
