import pandas as pd
import os

data_path = r"C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3"

files = ['event_details.csv', 'fight_details.csv', 'fighter_details.csv', 'UFC.csv']

for file in files:
    filepath = os.path.join(data_path, file)
    df = pd.read_csv(filepath)
    print(f"\n{'='*60}")
    print(f"File: {file}")
    print(f"{'='*60}")
    print(f"Shape: {df.shape}")
    print(f"\nColumns:\n{df.columns.tolist()}")
    print(f"\nFirst rows:")
    print(df.head(3))
    print(f"\nInfo:")
    print(df.info())
