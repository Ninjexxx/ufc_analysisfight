import pandas as pd
from data_loader import ensure_data

paths = ensure_data()

for name, filepath in paths.items():
    df = pd.read_csv(filepath)
    print(f"\n{'='*60}")
    print(f"File: {name} ({filepath})")
    print(f"{'='*60}")
    print(f"Shape: {df.shape}")
    print(f"\nColumns ({len(df.columns)}):\n{df.columns.tolist()[:15]}...")
    print(f"\nFirst rows:")
    print(df.head(2))
