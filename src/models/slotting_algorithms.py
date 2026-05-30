"""
Slotting Algorithms Module
--------------------------
This module contains the core algorithms for warehouse slotting optimization,
including traditional ABC Analysis and K-Means Clustering using Machine Learning.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ==========================================
# 1. TRADITIONAL ABC ANALYSIS
# ==========================================
def calculate_abc_classification(df: pd.DataFrame, metric_col: str = 'pick_frequency') -> pd.DataFrame:
    """
    Classifies SKUs into A, B, and C categories based on the Pareto Principle (80/20 rule).
    
    Category A: Top SKUs contributing to ~80% of total metric (e.g., pick frequency).
    Category B: Next SKUs contributing to ~15% (80% - 95%).
    Category C: Bottom SKUs contributing to the remaining ~5% (95% - 100%).

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset containing SKU features.
    metric_col : str
        The column name used for classification (default is 'pick_frequency').

    Returns:
    --------
    pandas.DataFrame
        The dataframe with a new column 'ABC_Class'.
    """
    # Create a copy to avoid SettingWithCopyWarning
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
    df_abc['ABC_Class'] = np.select(conditions, choices, default='C')
    
    # Drop the temporary cumulative percentage column to keep data clean
    df_abc = df_abc.drop(columns=['cum_percent'])
    
    return df_abc

# ==========================================
# 2. K-MEANS CLUSTERING (AI SLOTTING)
# ==========================================
def run_kmeans_clustering(df: pd.DataFrame, feature_cols: list, n_clusters: int = 3, random_state: int = 42) -> pd.DataFrame:
    """
    Applies K-Means clustering algorithm to group SKUs based on their features.

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataset containing SKU features.
    feature_cols : list
        List of column names to be used as features for clustering (e.g., ['qty', 'pick_frequency']).
    n_clusters : int
        The number of clusters (K) to form.
    random_state : int
        Seed for reproducibility.

    Returns:
    --------
    pandas.DataFrame
        The dataframe with a new column 'KMeans_Cluster' and the fitted K-Means model.
    """
    df_kmeans = df.copy()
    
    # Extract features for clustering
    X = df_kmeans[feature_cols]
    
    # Crucial Step: Feature Scaling
    # K-Means uses distance calculations internally, so scaling features is mandatory
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Initialize and fit the K-Means model
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=random_state)
    df_kmeans['KMeans_Cluster'] = kmeans.fit_predict(X_scaled)
    
    return df_kmeans, kmeans, scaler