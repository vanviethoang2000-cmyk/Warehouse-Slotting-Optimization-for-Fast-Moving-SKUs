"""
Simulation Engine Module
------------------------
Handles the heavy calculation of Manhattan distances for order picking routes.
"""

from src.utils.metrics import calculate_manhattan_distance

def simulate_order(order, layout, io_point=(0, 0)):
    """Simulates the picking route using Greedy Nearest Neighbor logic."""
    dist = 0
    curr = io_point
    
    # 1. Lọc ra tọa độ của các món hàng có trong đơn
    unvisited_targets = [layout[sku] for sku in order if sku in layout]
    
    # 2. Thuật toán Greedy: Vòng lặp tìm điểm gần nhất
    while unvisited_targets:
        # Dò tìm điểm có khoảng cách Manhattan ngắn nhất so với vị trí hiện tại (curr)
        closest_target = min(unvisited_targets, key=lambda target: calculate_manhattan_distance(curr, target))
        
        # Di chuyển tới đó và cộng dồn khoảng cách
        dist += calculate_manhattan_distance(curr, closest_target)
        curr = closest_target
        
        # Nhặt xong thì xóa khỏi danh sách chờ
        unvisited_targets.remove(closest_target)
        
    # 3. Lấy hàng xong, quay về điểm xuất phát I/O Point
    dist += calculate_manhattan_distance(curr, io_point)
    
    return dist

def run_full_simulation(real_orders, layout_kmeans, layout_abc, layout_random, io_point=(0, 0)):
    """Executes the simulation across all three warehouse layouts."""
    res_kmeans = [simulate_order(o, layout_kmeans, io_point) for o in real_orders]
    res_abc = [simulate_order(o, layout_abc, io_point) for o in real_orders]
    res_random = [simulate_order(o, layout_random, io_point) for o in real_orders]
    
    return res_kmeans, res_abc, res_random