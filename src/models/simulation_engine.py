"""
Simulation Engine Module
------------------------
Handles the heavy calculation of Manhattan distances for order picking routes.
"""

def calculate_manhattan_distance(p1, p2):
    """Calculates the distance between two (x, y) coordinates."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def simulate_order(order, layout, io_point=(0, 0)):
    """Simulates the picking route for a single order."""
    dist = 0
    curr = io_point
    for sku in order:
        if sku in layout:
            target = layout[sku]
            dist += calculate_manhattan_distance(curr, target)
            curr = target
    dist += calculate_manhattan_distance(curr, io_point) # Return to I/O point
    return dist

def run_full_simulation(real_orders, layout_kmeans, layout_abc, layout_random, io_point=(0, 0)):
    """Executes the simulation across all three warehouse layouts."""
    res_kmeans = [simulate_order(o, layout_kmeans, io_point) for o in real_orders]
    res_abc = [simulate_order(o, layout_abc, io_point) for o in real_orders]
    res_random = [simulate_order(o, layout_random, io_point) for o in real_orders]
    
    return res_kmeans, res_abc, res_random