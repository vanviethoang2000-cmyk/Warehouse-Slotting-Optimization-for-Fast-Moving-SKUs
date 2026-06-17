import pandas as pd

df = pd.read_csv(r"d:\Studying\AI FPT\2026 Summer\ADY301m\Project_finals\features\sku_features.csv")

result = (
    df["abc_class"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
    .reindex(["A", "B", "C"])
)

print(result)