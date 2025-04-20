from flask import Flask, request, jsonify

app = Flask(__name__)

# Define product locations
product_locations = {
    "A": "C1", "B": "C1", "C": "C1",
    "D": "C2", "E": "C2", "F": "C2",
    "G": "C3", "H": "C3", "I": "C3"
}

# Define travel costs
travel_costs = {
    ("C1", "L1"): 20,
    ("C2", "L1"): 30,
    ("C3", "L1"): 25,
    ("C1", "C2"): 15,
    ("C2", "C1"): 15,
    ("C1", "C3"): 10,
    ("C3", "C1"): 10,
    ("C2", "C3"): 15,
    ("C3", "C2"): 15,
    ("L1", "C1"): 20,
    ("L1", "C2"): 30,
    ("L1", "C3"): 25
}

def calculate_min_cost(order):
    # Identify centers that have the products
    centers_needed = set()
    for product, quantity in order.items():
        if quantity > 0:
            centers_needed.add(product_locations.get(product))

    if not centers_needed:
        return 0  # No items to deliver

    # Greedily pick the closest center to L1 as the starting point
    start_center = min(centers_needed, key=lambda center: travel_costs.get((center, "L1"), float('inf')))
    centers_needed.remove(start_center)

    total_cost = travel_costs.get((start_center, "L1"), 0)

    # Now, we need to figure out the most efficient way to visit all other centers
    # We’ll take the nearest center first and then continue picking the nearest available center.
    current_center = start_center

    while centers_needed:
        next_center = min(centers_needed, key=lambda center: travel_costs.get((current_center, center), float('inf')))
        total_cost += travel_costs.get((current_center, next_center), 0)  # Travel between centers
        current_center = next_center
        centers_needed.remove(next_center)

    # Finally, we must return to L1 after picking up all items
    total_cost += travel_costs.get((current_center, "L1"), 0)

    return total_cost

@app.route('/calculate-cost', methods=['POST'])
def calculate_cost():
    data = request.get_json()
    min_cost = calculate_min_cost(data)

    return jsonify({
        "message": "Delivery cost calculated!",
        "minimum_cost": min_cost
    })

if __name__ == '__main__':
    app.run(debug=True)
