import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv(r"C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\UFC.csv")

print(f"Total fights: {len(df)}")

df['r_win'] = (df['winner'] == df['r_name']).astype(int)

df['win_diff'] = df['r_wins'] - df['b_wins']
df['loss_diff'] = df['r_losses'] - df['b_losses']
df['height_diff'] = df['r_height'] - df['b_height']
df['reach_diff'] = df['r_reach'] - df['b_reach']
df['weight_diff'] = df['r_weight'] - df['b_weight']

df['r_win_rate'] = df['r_wins'] / (df['r_wins'] + df['r_losses'] + 1)
df['b_win_rate'] = df['b_wins'] / (df['b_wins'] + df['b_losses'] + 1)
df['win_rate_diff'] = df['r_win_rate'] - df['b_win_rate']

df['str_acc_diff'] = df['r_str_acc'] - df['b_str_acc']
df['str_def_diff'] = df['r_str_def'] - df['b_str_def']
df['td_avg_diff'] = df['r_td_avg'] - df['b_td_avg']
df['td_def_diff'] = df['r_td_def'] - df['b_td_def']
df['splm_diff'] = df['r_splm'] - df['b_splm']
df['sapm_diff'] = df['r_sapm'] - df['b_sapm']

features = [
    'r_wins', 'r_losses', 'r_height', 'r_weight', 'r_reach',
    'r_splm', 'r_str_acc', 'r_sapm', 'r_str_def', 
    'r_td_avg', 'r_td_avg_acc', 'r_td_def', 'r_sub_avg',
    'b_wins', 'b_losses', 'b_height', 'b_weight', 'b_reach',
    'b_splm', 'b_str_acc', 'b_sapm', 'b_str_def',
    'b_td_avg', 'b_td_avg_acc', 'b_td_def', 'b_sub_avg',
    'win_diff', 'loss_diff', 'height_diff', 'reach_diff', 'weight_diff',
    'r_win_rate', 'b_win_rate', 'win_rate_diff',
    'str_acc_diff', 'str_def_diff', 'td_avg_diff', 'td_def_diff',
    'splm_diff', 'sapm_diff'
]

df_model = df[features + ['r_win']].dropna()

X = df_model[features]
y = df_model['r_win']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTraining: {len(X_train)} fights")
print(f"Testing: {len(X_test)} fights")

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

print(f"\n{'='*60}")
print(f"XGBOOST MODEL RESULTS")
print(f"{'='*60}")
print(f"Accuracy: {accuracy:.2%}")
print(f"AUC-ROC: {auc:.4f}")
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Blue Corner', 'Red Corner']))

feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n{'='*60}")
print(f"TOP 15 MOST IMPORTANT FEATURES")
print(f"{'='*60}")
print(feature_importance.head(15).to_string(index=False))

import pickle
with open('ufc_xgboost_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(f"\nXGBoost model saved as 'ufc_xgboost_model.pkl'")
