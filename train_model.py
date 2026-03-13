import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv(r"C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\UFC.csv")

print(f"Total fights: {len(df)}")
print(f"\nDivisions: {df['division'].value_counts()}")

df['r_win'] = (df['winner'] == df['r_name']).astype(int)

features = [
    'r_wins', 'r_losses', 'r_height', 'r_weight', 'r_reach',
    'r_splm', 'r_str_acc', 'r_sapm', 'r_str_def', 
    'r_td_avg', 'r_td_avg_acc', 'r_td_def', 'r_sub_avg',
    'b_wins', 'b_losses', 'b_height', 'b_weight', 'b_reach',
    'b_splm', 'b_str_acc', 'b_sapm', 'b_str_def',
    'b_td_avg', 'b_td_avg_acc', 'b_td_def', 'b_sub_avg'
]

df_model = df[features + ['r_win']].dropna()

X = df_model[features]
y = df_model['r_win']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*60}")
print(f"MODEL RESULTS")
print(f"{'='*60}")
print(f"Accuracy: {accuracy:.2%}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Blue Corner', 'Red Corner']))

feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n{'='*60}")
print(f"TOP 10 MOST IMPORTANT FEATURES")
print(f"{'='*60}")
print(feature_importance.head(10).to_string(index=False))

import pickle
with open('ufc_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(f"\nModel saved as 'ufc_model.pkl'")
