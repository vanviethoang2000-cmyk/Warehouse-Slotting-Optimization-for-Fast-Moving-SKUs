import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

def extract_ml_features(input_path='../../data/processed/data_clean.csv', out_dir='../../features'):
    """
    Feature Engineering pipeline for Demand Forecasting.
    Strictly prevents Data Leakage and enforces Time-Series Alignment (Zero-Imputation).
    """
    print("[1/7] Loading dataset...")
    df = pd.read_csv(input_path)
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    # Create a mask to define the Train set (Prevent Data Leakage)
    train_mask = df['order_date'] <= '2010-10-31'
    
    print("[2/7] Generating Synthetic Promotion Proxy (Leakage-Free)...")
    # ONLY calculate median on Train set, then map to all SKUs
    train_median_price = df[train_mask].groupby('stock_code')['price'].median().rename('base_price')
    df = df.merge(train_median_price, on='stock_code', how='left')
    
    # If an SKU appears in the Test set (no base_price in Train), use its current price as base
    df['base_price'] = df['base_price'].fillna(df['price'])
    df['is_promo'] = (df['price'] < 0.9 * df['base_price']).astype(int)
    
    print("[3/7] Aggregating sales data to Daily level...")
    daily_sales = df.groupby(['stock_code', 'order_date']).agg(
        daily_quantity=('quantity', 'sum'),
        is_promo=('is_promo', 'max')
    ).reset_index()
    
    print("[4/7] Performing Outlier Capping (Leakage-Free)...")
    train_daily_mask = daily_sales['order_date'] <= '2010-10-31'
    
    # ONLY calculate the 99.5% ceiling (upper bound) on the Train set
    train_upper_bounds = daily_sales[train_daily_mask].groupby('stock_code')['daily_quantity'].quantile(0.995).rename('upper_bound')
    daily_sales = daily_sales.merge(train_upper_bounds, on='stock_code', how='left')
    
    # Fill new SKUs with a safe ceiling (e.g., its max value)
    daily_sales['upper_bound'] = daily_sales['upper_bound'].fillna(daily_sales['daily_quantity'].max())
    
    # Apply capping BEFORE Zero-Imputation to maintain statistical integrity
    daily_sales['daily_quantity'] = np.where(
        daily_sales['daily_quantity'] > daily_sales['upper_bound'], 
        daily_sales['upper_bound'], 
        daily_sales['daily_quantity']
    )
    
    print("[5/7] Time-Series Alignment & Zero-Imputation...")
    # CRITICAL FIX: Align dates to create a continuous calendar timeline
    min_date = daily_sales['order_date'].min()
    max_date = daily_sales['order_date'].max()
    
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    all_skus = daily_sales['stock_code'].unique()
    
    # Create a full matrix (SKUs x All Calendar Days)
    multi_idx = pd.MultiIndex.from_product([all_skus, all_dates], names=['stock_code', 'order_date'])
    aligned_sales = daily_sales.set_index(['stock_code', 'order_date']).reindex(multi_idx).reset_index()
    
    # Impute missing days with 0
    aligned_sales['daily_quantity'] = aligned_sales['daily_quantity'].fillna(0)
    aligned_sales['is_promo'] = aligned_sales['is_promo'].fillna(0)
    
    # Apply Logarithmic Compression AFTER aligning
    aligned_sales['daily_quantity'] = np.log1p(aligned_sales['daily_quantity'])
    
    print("[6/7] Extracting Seasonality & Autoregressive Features...")
    aligned_sales['month'] = aligned_sales['order_date'].dt.month
    aligned_sales['day_of_week'] = aligned_sales['order_date'].dt.dayofweek
    aligned_sales['is_weekend'] = aligned_sales['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Sort chronologically to ensure shift() works correctly
    aligned_sales = aligned_sales.sort_values(['stock_code', 'order_date'])
    
    aligned_sales['lag_1'] = aligned_sales.groupby('stock_code')['daily_quantity'].shift(1)
    aligned_sales['lag_3'] = aligned_sales.groupby('stock_code')['daily_quantity'].shift(3)
    aligned_sales['lag_7'] = aligned_sales.groupby('stock_code')['daily_quantity'].shift(7)
    
    aligned_sales['rolling_mean_7'] = aligned_sales.groupby('stock_code')['daily_quantity'].transform(
        lambda x: x.shift(1).rolling(window=7).mean()
    )
    
    print("[7/7] Splitting Train/Test and Exporting Data...")
    final_features = aligned_sales.dropna()
    
    # SPLIT THE DATASET FOR THE MODEL
    train_features = final_features[final_features['order_date'] <= '2010-10-31']
    test_features  = final_features[final_features['order_date'] >= '2010-11-01']
    
    # Drop intermediate columns not needed for ML
    cols_to_drop = ['upper_bound']
    if 'upper_bound' in train_features.columns:
        train_features = train_features.drop(columns=cols_to_drop)
        test_features = test_features.drop(columns=cols_to_drop)
    
    # Ensure output directory exists before exporting
    os.makedirs(out_dir, exist_ok=True)
    
    # Export files directly using Pandas
    train_path = f"{out_dir}/train_ml_features.csv"
    test_path = f"{out_dir}/test_ml_features.csv"
    
    train_features.to_csv(train_path, index=False)
    test_features.to_csv(test_path, index=False)
    
    print("=====================================================")
    print(" ✅ PIPELINE COMPLETE: TIME-SERIES ALIGNED & LEAKAGE PREVENTED!")
    print(f" -> Train Features saved to: {train_path} ({train_features.shape[0]:,} rows)")
    print(f" -> Test Features saved to:  {test_path} ({test_features.shape[0]:,} rows)")
    print("=====================================================\n")
    
    return train_features, test_features

# =====================================================================
# EXECUTE PIPELINE WHEN RUNNING THIS FILE DIRECTLY
# =====================================================================
if __name__ == "__main__":
    print("🚀 Starting Feature Engineering process...")
    
    # Call the function to run with default paths
    train_data, test_data = extract_ml_features()
    
    print("✅ Successfully extracted features for both Train and Test sets!")