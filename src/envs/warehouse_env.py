"""
Warehouse Environment Module
----------------------------
Sets up the virtual warehouse grid, handles coordinates, and loads the
clustered SKU data for the slotting simulation.
"""

import pandas as pd
import numpy as np

# =====================================================================
# 1. READ AGGREGATED SKU DATA (WITH K-MEANS CLUSTERS)
# =====================================================================
try:
    # Load the final dataset exported from the clustering stage
    df_skus = pd.read_csv('../../features/sku_clusters_final.csv')
    
    # VERY IMPORTANT: Sort SKUs by pick_frequency (highest first)
    # This ensures our simulation assigns the best slots to the fastest-moving items
    df_skus = df_skus.sort_values(by='pick_frequency', ascending=False).reset_index(drop=True)
    
    skus = df_skus['stock_code'].unique()
    print(f"[v] Successfully loaded {len(skus)} SKUs for slotting.")
except FileNotFoundError:
    print("[!] Error: File not found. Please ensure 'sku_clusters_final.csv' exists.")
    df_skus = pd.DataFrame()
    skus = []

# =====================================================================
# 2. ESTABLISH WAREHOUSE GRID AS A DICTIONARY (EFFICIENT LOOKUP)
# =====================================================================
WAREHOUSE_ROWS = 50
WAREHOUSE_COLS = 85  
io_point = (0, 0) # I/O point (Warehouse entrance/exit/dispatch area)

# Grid stores coordinate mapping with their status
# Using Dictionary instead of List for O(1) fast lookups during simulation
warehouse_grid = { 
    (x, y): {'status': 'Empty', 'sku': None, 'cluster': None} 
    for x in range(WAREHOUSE_ROWS) 
    for y in range(WAREHOUSE_COLS) 
}

if len(skus) > 0:
    print(f"[v] Virtual warehouse created with {len(warehouse_grid)} shelf positions.")
    print(f"[v] I/O point coordinates: {io_point}")
    print(f"[v] Safe capacity check: {'PASSED' if len(warehouse_grid) >= len(skus) else 'FAILED'}")

# =====================================================================
# 3. MANHATTAN DISTANCE FUNCTION
# =====================================================================
def calculate_manhattan_distance(pos1, pos2):
    """Calculates the Manhattan distance between two grid coordinates."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# =====================================================================
# 4. PRE-CALCULATE SORTED POSITIONS BY DISTANCE TO I/O POINT
# =====================================================================
# This list helps the algorithm quickly grab the absolute closest available slot
sorted_positions = sorted(
    warehouse_grid.keys(), 
    key=lambda pos: calculate_manhattan_distance(io_point, pos)
)

if len(skus) > 0:
    print(f"[v] Calculated distances for all positions.")
    print(f"    -> Closest slot: {sorted_positions[0]}")
    print(f"    -> Farthest slot: {sorted_positions[-1]}")
print("="*70)