-- Bước 1: Tính Doanh số, Vận tốc tháng và Tần suất nhặt hàng theo từng SKU
WITH SKU_Stats AS (
    SELECT 
        [stock_code],
        [category],
        -- Tính tổng doanh số
        SUM([quantity] * [price]) AS total_sales,
        
        -- Tính Velocity theo tháng (Tổng số lượng / Số tháng phát sinh giao dịch)
        -- Dùng DATEDIFF đếm số tháng từ ngày đầu đến ngày cuối của SKU đó
        SUM([quantity]) / (DATEDIFF(month, MIN([order_date]), MAX([order_date])) + 1.0) AS monthly_velocity,
        
        -- Đếm số lần đi lấy hàng (pick time)
        COUNT(DISTINCT [invoice_no]) AS pick_frequency
    FROM cleaned_online_retail
    GROUP BY [stock_code], [category]
),

-- Bước 2: Chuẩn bị tính % doanh số cộng dồn cho phân loại ABC
ABC_Prep AS (
    SELECT 
        [stock_code],
        [category],
        total_sales,
        monthly_velocity,
        pick_frequency,
        SUM(total_sales) OVER (ORDER BY total_sales DESC) AS cumulative_sales,
        SUM(total_sales) OVER () AS grand_total_sales
    FROM SKU_Stats
),

-- Bước 3: Phân loại ABC và Tính Slotting Score
SKU_Scoring AS (
    SELECT 
        [stock_code],
        [category],
        total_sales,
        monthly_velocity,
        pick_frequency,
        
        -- Phân hạng ABC (A: Top 80% doanh số, B: 15% tiếp theo, C: còn lại)
        CASE 
            WHEN cumulative_sales / NULLIF(grand_total_sales, 0) <= 0.80 THEN 'A'
            WHEN cumulative_sales / NULLIF(grand_total_sales, 0) <= 0.95 THEN 'B'
            ELSE 'C'
        END AS abc_class,
        
        -- Slotting score dựa 100% vào velocity (vì mình đã thống nhất drop size)
        monthly_velocity AS slotting_score
    FROM ABC_Prep
)

-- Bước 4: Xuất Top SKU theo Category và thời gian/tần suất pick
SELECT 
    [category],
    [stock_code],
    abc_class,
    monthly_velocity,
    pick_frequency,
    total_sales,
    slotting_score,
    -- Xếp hạng SKU trong từng Category, ưu tiên hàng lấy nhiều nhất (pick_frequency cao)
    RANK() OVER (PARTITION BY [category] ORDER BY pick_frequency DESC) AS rank_in_category
FROM SKU_Scoring
ORDER BY [category], rank_in_category;