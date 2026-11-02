import pandas as pd
import numpy as np
import pickle
import warnings
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, brier_score_loss
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

from calculate_elo import calculate_elo_ratings, save_elo_ratings
from feature_engineering import FEATURE_COLS, build_training_features, create_symmetric_dataset

warnings.filterwarnings('ignore')

def train_and_evaluate():
    print("="*60)
    print("1. CALCULANDO ELO HISTÓRICO E CARREGANDO DADOS")
    print("="*60)
    elo_ratings, elo_history, df_raw = calculate_elo_ratings()
    save_elo_ratings(elo_ratings, elo_history, output_dir='data')
    
    print(f"Total de lutas brutas: {len(df_raw)}")
    
    # 2. Engenharia de Atributos
    print("\n" + "="*60)
    print("2. ENGENHARIA DE ATRIBUTOS E LIMPEZA")
    print("="*60)
    df_clean = df_raw.dropna(subset=['winner', 'r_name', 'b_name']).copy()
    df_clean['target'] = (df_clean['winner'] == df_clean['r_name']).astype(int)
    df_features = build_training_features(df_clean)
    
    df_model = df_features[FEATURE_COLS + ['target', 'date']].dropna()
    print(f"Lutas válidas após limpeza: {len(df_model)}")
    
    # 3. Divisão Temporal (Out-of-Time Validation)
    split_date = '2023-01-01'
    train_mask = df_model['date'] < split_date
    test_mask = df_model['date'] >= split_date
    
    df_train = df_model[train_mask].copy()
    df_test = df_model[test_mask].copy()
    
    print(f"Lutas de Treino (< {split_date}): {len(df_train)}")
    print(f"Lutas de Teste (>= {split_date}): {len(df_test)}")
    
    # 4. Augmentation para Simetria de Corner (Neutralização de Viés)
    print("\n" + "="*60)
    print("3. APLICANDO SIMETRIA DE CORNER NO TREINO (DATA AUGMENTATION)")
    print("="*60)
    df_train_sym = create_symmetric_dataset(df_train, FEATURE_COLS)
    print(f"Total de amostras de treino simétrico: {len(df_train_sym)}")
    
    X_train = df_train_sym[FEATURE_COLS]
    y_train = df_train_sym['target']
    
    X_test = df_test[FEATURE_COLS]
    y_test = df_test['target']
    
    # 5. Treinamento do XGBoost Base
    print("\n" + "="*60)
    print("4. TREINANDO XGBOOST CLASSIFIER")
    print("="*60)
    base_xgb = xgb.XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.5,
        random_state=42,
        eval_metric='logloss'
    )
    base_xgb.fit(X_train, y_train)
    
    raw_pred = base_xgb.predict(X_test)
    raw_prob = base_xgb.predict_proba(X_test)[:, 1]
    raw_conf = np.maximum(raw_prob, 1 - raw_prob)
    
    # 6. Calibração de Probabilidades (Platt Scaling)
    print("\n" + "="*60)
    print("5. CALIBRANDO PROBABILIDADES COM CALIBRATEDCLASSIFIERCV")
    print("="*60)
    calibrated_model = CalibratedClassifierCV(base_xgb, method='sigmoid', cv=5)
    calibrated_model.fit(X_train, y_train)
    
    cal_pred = calibrated_model.predict(X_test)
    cal_prob = calibrated_model.predict_proba(X_test)[:, 1]
    cal_conf = np.maximum(cal_prob, 1 - cal_prob)
    
    # 7. Comparativo Estatístico
    print("\n" + "="*60)
    print("COMPARATIVO ESTATÍSTICO NO CONJUNTO DE TESTE TEMPORAL (2023-2025)")
    print("="*60)
    print(f"{'Métrica':<30} | {'XGBoost Bruto':<15} | {'XGBoost Calibrado':<15}")
    print("-"*66)
    print(f"{'Acurácia':<30} | {accuracy_score(y_test, raw_pred):<15.2%} | {accuracy_score(y_test, cal_pred):<15.2%}")
    print(f"{'AUC-ROC':<30} | {roc_auc_score(y_test, raw_prob):<15.4f} | {roc_auc_score(y_test, cal_prob):<15.4f}")
    print(f"{'Brier Score (Menor = melhor)':<30} | {brier_score_loss(y_test, raw_prob):<15.4f} | {brier_score_loss(y_test, cal_prob):<15.4f}")
    print(f"{'Confiança Média':<30} | {raw_conf.mean():<15.1%} | {cal_conf.mean():<15.1%}")
    print(f"{'% Predições com Confiança >90%':<30} | {(raw_conf > 0.90).mean():<15.1%} | {(cal_conf > 0.90).mean():<15.1%}")
    print(f"{'% Predições Disputadas (50-60%)':<30} | {((raw_conf >= 0.50) & (raw_conf <= 0.60)).mean():<15.1%} | {((cal_conf >= 0.50) & (cal_conf <= 0.60)).mean():<15.1%}")
    
    print("\nClassification Report (Modelo Calibrado):")
    print(classification_report(y_test, cal_pred, target_names=['Derrota Red', 'Vitória Red']))
    
    # Importância de Features
    importance_df = pd.DataFrame({
        'feature': FEATURE_COLS,
        'importance': base_xgb.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTOP 12 FEATURES MAIS IMPORTANTES:")
    print("="*60)
    for idx, row in importance_df.head(12).reset_index().iterrows():
        print(f"{idx+1:2d}. {row['feature']:<25} ({row['importance']:.4f})")
    
    # Salvar modelos
    with open('ufc_xgboost_model.pkl', 'wb') as f:
        pickle.dump(calibrated_model, f)
        
    with open('ufc_feature_names.pkl', 'wb') as f:
        pickle.dump(FEATURE_COLS, f)
        
    print("\nModelo calibrado salvo em 'ufc_xgboost_model.pkl' com sucesso!")
    return calibrated_model

if __name__ == '__main__':
    train_and_evaluate()
