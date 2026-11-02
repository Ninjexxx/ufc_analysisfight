import pandas as pd
import numpy as np
import pickle
import warnings
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

from data_loader import load_fights_df
from calculate_elo import calculate_elo_ratings
from feature_engineering import FEATURE_COLS, build_training_features, create_symmetric_dataset

warnings.filterwarnings('ignore')

def train_random_forest():
    print("="*60)
    print("TREINANDO RANDOM FOREST BASELINE")
    print("="*60)
    
    elo_ratings, _, df_raw = calculate_elo_ratings()
    df_clean = df_raw.dropna(subset=['winner', 'r_name', 'b_name']).copy()
    df_clean['target'] = (df_clean['winner'] == df_clean['r_name']).astype(int)
    
    df_features = build_training_features(df_clean)
    df_model = df_features[FEATURE_COLS + ['target', 'date']].dropna()
    
    # Split temporal
    train_mask = df_model['date'] < '2023-01-01'
    test_mask = df_model['date'] >= '2023-01-01'
    
    df_train_sym = create_symmetric_dataset(df_model[train_mask], FEATURE_COLS)
    
    X_train = df_train_sym[FEATURE_COLS]
    y_train = df_train_sym['target']
    X_test = df_model.loc[test_mask, FEATURE_COLS]
    y_test = df_model.loc[test_mask, 'target']
    
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    
    print(f"\nRandom Forest Acurácia: {acc:.2%}")
    print(f"Random Forest AUC-ROC: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Derrota Red', 'Vitória Red']))
    
    with open('ufc_model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    print("Modelo salvo como 'ufc_model.pkl'")
    return model

if __name__ == '__main__':
    train_random_forest()
