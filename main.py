from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
from itertools import permutations
import math

app = FastAPI()

# Product details from PDF
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

# Distance table (bi‑directional)
DIST = {
    "C1": {"L1": 3, "C2": 4, "C3": 3},
    "C2": {"L1": 2, "C1": 4, "C3": 3},
    "C3": {"L1": 2, "C1": 3, "C2": 3},
    "L1": {"C1": 3, "C2": 2, "C3": 2}
}

class Order(BaseModel):
    A: int = 0; B: int = 0; C: int = 0
    D: int = 0; E: int = 0; F: int = 0
    G: int = 0; H: int = 0; I: int = 0

def slab_rate(w: float) -> float:
    if w <= 5:
        return 10
    extra = w - 5
    slabs = math.ceil(extra / 5)
    return 10 + slabs * 8

@app.post("/calculate-cost")
def calculate_cost(order: Order):
    data = order.dict()

    # 1) Compute weight at each center
    center_w: Dict[str, float] = {}
    for p, qty in data.items():
        if qty > 0:
            c = PRODUCT_CENTER[p]
            center_w[c] = center_w.get(c, 0) + PRODUCT_WEIGHT[p] * qty

    centers = list(center_w.keys())
    best = float("inf")

    # 2) Try each start center and order of other centers
    for start in centers:
        others = [c for c in centers if c != start]
        for perm in permutations(others):
            cost = 0
            # Leg 1: start -> L1 (pickup & deliver start)
            w0 = center_w[start]
            cost += DIST[start]["L1"] * slab_rate(w0)

            # For each next center in perm:
            for c in perm:
                # empty return: L1 -> c
                cost += DIST["L1"][c] * slab_rate(0)
                # pickup & deliver: c -> L1
                wc = center_w[c]
                cost += DIST[c]["L1"] * slab_rate(wc)

            best = min(best, cost)

    return {"minimum_cost": round(best)}
