import os
import sys
import pickle
import pandas as pd
import numpy as np

from data_loader import ensure_data, load_fighters_df
from test_predictions import get_weight_class, weight_classes_compatible, predict_fight

def test_files_exist():
    """Testa se os arquivos necessários existem."""
    print("\n" + "="*60)
    print("TESTE 1: Verificação de arquivos necessários")
    print("="*60)
    
    paths = ensure_data()
    files = {
        'ufc_xgboost_model.pkl': 'Modelo XGBoost Calibrado',
        'ufc_model.pkl': 'Modelo Random Forest Baseline',
        paths['fighter_details']: 'Dataset de Lutadores',
        paths['ufc']: 'Dataset de Lutas UFC'
    }
    
    all_exist = True
    for file, desc in files.items():
        exists = os.path.exists(file)
        status = "[OK]" if exists else "[AUSENTE]"
        print(f"{status} - {desc} ({file})")
        if not exists:
            all_exist = False
            
    return all_exist

def test_model_loading():
    """Testa o carregamento do modelo XGBoost."""
    print("\n" + "="*60)
    print("TESTE 2: Carregamento do modelo")
    print("="*60)
    
    try:
        with open('ufc_xgboost_model.pkl', 'rb') as f:
            model = pickle.load(f)
        print(f"[OK] Modelo carregado com sucesso: {type(model).__name__}")
        return True, model
    except Exception as e:
        print(f"[ERRO] Erro ao carregar modelo: {e}")
        return False, None

def test_data_loading():
    """Testa o carregamento dos datasets."""
    print("\n" + "="*60)
    print("TESTE 3: Carregamento dos dados")
    print("="*60)
    
    try:
        fighters_df = load_fighters_df()
        print(f"[OK] Dataset carregado: {len(fighters_df)} lutadores")
        return True, fighters_df
    except Exception as e:
        print(f"[ERRO] Erro ao carregar dados: {e}")
        return False, None

def test_predictions_cases():
    """Testa predições em confrontos conhecidos."""
    print("\n" + "="*60)
    print("TESTE 4: Teste de predições")
    print("="*60)
    
    test_cases = [
        ("Jon Jones", "Stipe Miocic"),
        ("Islam Makhachev", "Charles Oliveira"),
        ("Alex Pereira", "Israel Adesanya")
    ]
    
    success = 0
    for f1, f2 in test_cases:
        res = predict_fight(f1, f2)
        if res and res.get('winner'):
            print(f"[OK] {f1} vs {f2} -> Vencedor: {res['winner']} ({res['confidence']:.1f}%)")
            success += 1
        else:
            print(f"[FALHA] Falha na predição: {f1} vs {f2}")
            
    return success == len(test_cases)

def test_weight_validation():
    """Testa a validação das categorias de peso."""
    print("\n" + "="*60)
    print("TESTE 5: Validação de categorias de peso")
    print("="*60)
    
    c1 = get_weight_class(65.0)  # Featherweight
    c2 = get_weight_class(93.0)  # Heavyweight / Light Heavyweight
    print(f"[OK] 65kg -> {c1}")
    print(f"[OK] 93kg -> {c2}")
    
    compatible = weight_classes_compatible(70.31, 77.11)
    incompatible = weight_classes_compatible(70.31, 92.99)
    
    print(f"[OK] Leve (70.3kg) vs Meio-Médio (77.1kg): {'Compatível' if compatible else 'Incompatível'}")
    print(f"[OK] Leve (70.3kg) vs Meio-Pesado (93kg): {'Incompatível' if not incompatible else 'Falha'}")
    
    return compatible and not incompatible

def test_symmetry():
    """Testa a simetria de predições (invariância ao corner)."""
    print("\n" + "="*60)
    print("TESTE 6: Teste de Simetria de Predição")
    print("="*60)
    
    res1 = predict_fight("Jon Jones", "Stipe Miocic")
    res2 = predict_fight("Stipe Miocic", "Jon Jones")
    
    prob_jones_1 = res1['prob_f1']
    prob_jones_2 = res2['prob_f2']
    diff = abs(prob_jones_1 - prob_jones_2)
    
    print(f"P(Jones como F1): {prob_jones_1*100:.2f}%")
    print(f"P(Jones como F2): {prob_jones_2*100:.2f}%")
    print(f"Diferença de simetria: {diff*100:.2f}%")
    
    is_symmetric = diff < 0.05
    if is_symmetric:
        print("[OK] Simetria aprovada (diferença < 5%)")
    else:
        print("[FALHA] Assimetria excessiva detectada")
    return is_symmetric

def main():
    print("="*60)
    print("SUÍTE DE TESTES AUTOMATIZADOS - UFC PREDICTION SYSTEM")
    print("="*60)
    
    tests = [
        ("Arquivos necessários", test_files_exist()),
    ]
    
    m_ok, _ = test_model_loading()
    tests.append(("Carregamento do modelo", m_ok))
    
    d_ok, _ = test_data_loading()
    tests.append(("Carregamento dos dados", d_ok))
    
    if m_ok and d_ok:
        tests.append(("Predições", test_predictions_cases()))
        tests.append(("Validação de categorias", test_weight_validation()))
        tests.append(("Simetria de predição", test_symmetry()))
        
    print("\n" + "="*60)
    print("SUMÁRIO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)
    
    for name, ok in tests:
        status = "[PASSOU]" if ok else "[FALHOU]"
        print(f"{status} - {name}")
        
    print(f"\n{passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    return passed == total

if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
