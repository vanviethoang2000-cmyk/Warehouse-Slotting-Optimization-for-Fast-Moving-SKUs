SELECT 
    [stock_code],
    [category],
    -- Tách năm và tháng ra làm 2 cột riêng biệt để sau này dễ đưa vào model Machine Learning
    YEAR([order_date]) AS order_year,
    MONTH([order_date]) AS order_month,
    
    -- Đây chính là "Biến mục tiêu" (Target Variable - Y) cho mô hình dự báo
    SUM([quantity]) AS monthly_quantity,
    
    -- Tính thêm doanh thu và tần suất nhặt hàng theo từng tháng để làm Heatmap (Stage 1.4)
    SUM([quantity] * [price]) AS monthly_sales,
    COUNT(DISTINCT [invoice_no]) AS monthly_pick_frequency
FROM cleaned_online_retail
GROUP BY 
    [stock_code],
    [category],
    YEAR([order_date]),
    MONTH([order_date])
ORDER BY 
    [stock_code], 
    order_year, 
    order_month;