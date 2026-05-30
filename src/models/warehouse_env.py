import pandas as pd
import numpy as np

# 1. READ STATIC DATA
# Change the path if your file is located in a different directory
try:
    df_features = pd.read_csv('features/sku_features.csv')
    skus = df_features['stock_code'].unique()
    print(f"Total SKUs to be slotted: {len(skus)}")
except FileNotFoundError:
    print("Error: File not found. Please check the path!")
    skus = []

# 2. ESTABLISH WAREHOUSE COORDINATE GRID (GRID LAYOUT)
def create_warehouse_grid(rows, cols):
    grid = []
    for x in range(rows):
        for y in range(cols):
            grid.append((x, y))
    return grid

# Warehouse dimensions 50x85 = 4250 positions (Ensures capacity > SKU count)
WAREHOUSE_ROWS = 50
WAREHOUSE_COLS = 85  
warehouse_positions = create_warehouse_grid(WAREHOUSE_ROWS, WAREHOUSE_COLS)
io_point = (0, 0) # I/O point (Warehouse entrance/exit)

if len(skus) > 0:
    print(f"Virtual warehouse successfully created with {len(warehouse_positions)} shelf positions.")
    print(f"I/O point coordinates: {io_point}")
    print(f"Safe capacity: {len(warehouse_positions) >= len(skus)}")

# 3. MANHATTAN DISTANCE FUNCTION
def calculate_manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# Test the distance function
sample_shelf = (10, 25)
dist = calculate_manhattan_distance(io_point, sample_shelf)
print(f"-> Test: Distance from I/O point {io_point} to shelf {sample_shelf} is {dist} steps.")