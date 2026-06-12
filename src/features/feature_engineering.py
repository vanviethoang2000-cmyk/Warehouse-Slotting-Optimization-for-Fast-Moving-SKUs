import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def extract_ml_features(input_path='../../data/processed/data_clean.csv', out_dir='../../features'):
    """
    Feature Engineering pipeline for Demand Forecasting.
    Strictly prevents Data Leakage by calculating parameters ONLY on the Training window.
    """
    print("[1/6] Loading dataset...")
    df = pd.read_csv(input_path)
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    
    # Tạo mặt nạ chỉ định tập Train (Chống Data Leakage)
    train_mask = df['order_date'] <= '2010-10-31'
    
    print("[2/6] Generating Synthetic Promotion Proxy (Leakage-Free)...")
    # CHỈ tính median trên tập Train, sau đó map lại cho toàn bộ SKU
    train_median_price = df[train_mask].groupby('stock_code')['price'].median().rename('base_price')
    df = df.merge(train_median_price, on='stock_code', how='left')
    
    # Nếu SKU nào ở tập Test mới xuất hiện (chưa có base_price ở Train), dùng giá hiện tại làm base
    df['base_price'] = df['base_price'].fillna(df['price'])
    df['is_promo'] = (df['price'] < 0.9 * df['base_price']).astype(int)
    
    print("[3/6] Aggregating sales data to Daily level...")
    daily_sales = df.groupby(['stock_code', 'order_date']).agg(
        daily_quantity=('quantity', 'sum'),
        is_promo=('is_promo', 'max')
    ).reset_index()
    
    print("[3.5/6] Performing Outlier Capping & Log Transform (Leakage-Free)...")
    train_daily_mask = daily_sales['order_date'] <= '2010-10-31'
    
    # CHỈ tính mức trần 99.5% trên tập Train
    train_upper_bounds = daily_sales[train_daily_mask].groupby('stock_code')['daily_quantity'].quantile(0.995).rename('upper_bound')
    daily_sales = daily_sales.merge(train_upper_bounds, on='stock_code', how='left')
    
    # Fill các SKU mới bằng một mức trần an toàn (ví dụ: max của nó)
    daily_sales['upper_bound'] = daily_sales['upper_bound'].fillna(daily_sales['daily_quantity'].max())
    
    # Cắt ngọn và Nén Logarit
    daily_sales['daily_quantity'] = np.where(
        daily_sales['daily_quantity'] > daily_sales['upper_bound'], 
        daily_sales['upper_bound'], 
        daily_sales['daily_quantity']
    )
    daily_sales['daily_quantity'] = np.log1p(daily_sales['daily_quantity'])
    
    print("[4/6] Extracting Seasonality Features...")
    daily_sales['month'] = daily_sales['order_date'].dt.month
    daily_sales['day_of_week'] = daily_sales['order_date'].dt.dayofweek
    daily_sales['is_weekend'] = daily_sales['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    print("[5/6] Building Autoregressive Features (Lag & Rolling)...")
    daily_sales = daily_sales.sort_values(['stock_code', 'order_date'])
    
    daily_sales['lag_1'] = daily_sales.groupby('stock_code')['daily_quantity'].shift(1)
    daily_sales['lag_3'] = daily_sales.groupby('stock_code')['daily_quantity'].shift(3)
    daily_sales['lag_7'] = daily_sales.groupby('stock_code')['daily_quantity'].shift(7)
    
    daily_sales['rolling_mean_7'] = daily_sales.groupby('stock_code')['daily_quantity'].transform(
        lambda x: x.shift(1).rolling(window=7).mean()
    )
    
    print("[6/6] Splitting Train/Test and Exporting Data...")
    daily_sales_clean = daily_sales.dropna()
    
    # CHIA TÁCH TẬP DỮ LIỆU ĐỂ ĐƯA VÀO MODEL
    train_features = daily_sales_clean[daily_sales_clean['order_date'] <= '2010-10-31']
    test_features  = daily_sales_clean[daily_sales_clean['order_date'] >= '2010-11-01']
    
    # Drop các cột trung gian không cần cho ML
    cols_to_drop = ['upper_bound']
    train_features = train_features.drop(columns=cols_to_drop)
    test_features = test_features.drop(columns=cols_to_drop)
    
    # Xuất file thẳng bằng Pandas (Đường dẫn dùng ../../ vì gọi từ notebook)
    train_path = f"{out_dir}/train_ml_features.csv"
    test_path = f"{out_dir}/test_ml_features.csv"
    
    train_features.to_csv(train_path, index=False)
    test_features.to_csv(test_path, index=False)
    
    print("=====================================================")
    print(" ✅ PIPELINE COMPLETE: STRICT LEAKAGE PREVENTION APPLIED!")
    print(f" -> Train Features saved to: {train_path} ({train_features.shape[0]:,} rows)")
    print(f" -> Test Features saved to:  {test_path} ({test_features.shape[0]:,} rows)")
    print("=====================================================\n")
    
    return train_features, test_features

# =====================================================================
# THỰC THI PIPELINE KHI CHẠY TRỰC TIẾP FILE NÀY
# =====================================================================
if __name__ == "__main__":
    print("🚀 Bắt đầu tiến trình Feature Engineering (Chống Data Leakage)...")
    
    # Gọi hàm ra để chạy với đường dẫn mặc định
    train_data, test_data = extract_ml_features()
    
    print("✅ Đã trích xuất xong đặc trưng cho cả tập Train và Test!")