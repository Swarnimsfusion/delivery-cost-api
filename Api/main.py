from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict

app = FastAPI(
    title="Delivery Cost API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# Warehouse stock data
center_stock = {
    "C1": {"A": 3, "B": 2, "C": 8, "D": 12},
    "C2": {"E": 25, "F": 15},
    "C3": {"G": 0.5, "H": 1, "I": 2}
}

# Distance graph (center to center or to L1)
distances = {
    ("C1", "L1"): 3,
    ("C2", "L1"): 2.5,
    ("C3", "L1"): 2,
    ("C1", "C2"): 4,
    ("C2", "C1"): 4,
    ("C1", "C3"): 3,
    ("C3", "C1"): 3,
    ("C2", "C3"): 2.5,
    ("C3", "C2"): 2.5,
}

# Cost slab
def calculate_cost(weight, distance):
    cost = 0
    while weight > 0:
        if weight <= 5:
            cost += 10 * distance
            break
        else:
            cost += 8 * distance
            weight -= 5
    return cost

class OrderRequest(BaseModel):
    __root__: Dict[str, int]

@app.post("/calculate-cost")
def calculate_cost_endpoint(order: OrderRequest):
    order = order.__root__
    # Simplified logic: get from respective centers
    routes = []
    for center, stock in center_stock.items():
        total_weight = 0
        for product, qty in order.items():
            if product in stock:
                total_weight += stock[product] * qty
        if total_weight > 0:
            distance = distances.get((center, "L1"), 999)
            cost = calculate_cost(total_weight, distance)
            routes.append(cost)

    return {"minimum_cost": min(routes) if routes else 0}
