import pandas as pd

# Load the raw viewing logs (bronze layer)
bronze_logs = pd.read_csv('data/bronze_layer/dish_viewing_logs.csv')
print("=== BRONZE LAYER (Raw) ===")
print(f"Total Records: {len(bronze_logs)}")
print(f"Unique Genres: {bronze_logs['Program_Genre'].nunique()}")
print("\nGenre Breakdown:")
print(bronze_logs['Program_Genre'].value_counts())

# Load the gold layer
gold_content = pd.read_csv('data/gold_layer/gold_content_strategy.csv')
print("\n=== GOLD LAYER (Processed) ===")
print(f"Total Records: {len(gold_content)}")
print(f"Unique Genres: {gold_content['Program_Genre'].nunique()}")
print("\nGenre Breakdown:")
print(gold_content['Program_Genre'].value_counts())
