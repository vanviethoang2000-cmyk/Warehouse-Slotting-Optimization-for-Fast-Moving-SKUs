"""
Slotting Algorithms Module
--------------------------
This module contains the core algorithms for warehouse slotting optimization,
including traditional ABC Analysis and K-Means Clustering using Machine Learning.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import RobustScaler # UPGRADED: Handles outliers much better than StandardScaler

# =====================================================================
# 1. TRADITIONAL ABC ANALYSIS
# =====================================================================
def calculate_abc_classification(df: pd.DataFrame, metric_col: str = 'pick_frequency') -> pd.DataFrame:
    """
    Classifies SKUs into A, B, and C categories based on the Pareto Principle (80/20 rule).
    
    Category A: Top SKUs contributing to ~80% of total metric (e.g., pick frequency).
    Category B: Next SKUs contributing to ~15% (80% - 95%).
    Category C: Bottom SKUs contributing to the remaining ~5% (95% - 100%).
    """
    df_abc = df.copy()
    
    # Step 1: Sort the dataframe in descending order based on the metric
    df_abc = df_abc.sort_values(by=metric_col, ascending=False).reset_index(drop=True)
    
    # Step 2: Calculate cumulative percentage
    total_metric = df_abc[metric_col].sum()
    df_abc['cum_percent'] = (df_abc[metric_col].cumsum() / total_metric) * 100
    
    # Step 3: Define conditions for A, B, C classes
    conditions = [
        (df_abc['cum_percent'] <= 80),
        (df_abc['cum_percent'] > 80) & (df_abc['cum_percent'] <= 95),
        (df_abc['cum_percent'] > 95)
    ]
    choices = ['A', 'B', 'C']
    
    # Step 4: Apply the classification
    df_abc['abc_class'] = np.select(conditions, choices, default='C')
    
    # Drop the temporary column to keep data clean
    df_abc = df_abc.drop(columns=['cum_percent'])
    
    return df_abc

# =====================================================================
# 2. K-MEANS CLUSTERING (AI SLOTTING)
# =====================================================================
def run_kmeans_clustering(df: pd.DataFrame, feature_cols: list, n_clusters: int = 3, random_state: int = 42):
    """
    Applies K-Means clustering algorithm to group SKUs based on their features.
    Upgraded to use RobustScaler to handle heavy outliers in warehouse data.
    """
    df_kmeans = df.copy()
    
    # Extract features for clustering
    X = df_kmeans[feature_cols]
    
    # Crucial Step: Feature Scaling using RobustScaler
    # Warehouse data (like pick frequency and volume) typically has massive outliers.
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Initialize and fit the K-Means model
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=random_state, n_init=10)
    df_kmeans['cluster_label'] = kmeans.fit_predict(X_scaled)
    
    return df_kmeans, kmeans, scaler