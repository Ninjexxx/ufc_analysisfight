import os
import pickle
import numpy as np
import pandas as pd

from data_loader import load_fighters_df, ensure_data
from calculate_elo import calculate_elo_ratings, get_fighter_elo
from feature_engineering import extract_matchup_features

# 1. Carregamento do modelo XGBoost calibrado
MODEL_PATH = 'ufc_xgboost_model.pkl'
if not os.path.exists(MODEL_PATH):
    from train_xgboost import train_and_evaluate
    print("Modelo 'ufc_xgboost_model.pkl' não encontrado. Treinando automaticamente...")
    train_and_evaluate()

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# 2. Carregamento dos lutadores e ratings Elo
fighters_df = load_fighters_df()

ELO_CSV = os.path.join('data', 'fighter_elo_ratings.csv')
if os.path.exists(ELO_CSV):
    elo_df = pd.read_csv(ELO_CSV)
    elo_ratings = dict(zip(elo_df['fighter'], elo_df['elo_rating']))
else:
    elo_ratings, _, _ = calculate_elo_ratings()

# UFC Weight Classes (in kg)
WEIGHT_CLASSES = {
    'Strawweight': (0, 52.16),
    'Flyweight': (52.17, 56.70),
    'Bantamweight': (56.71, 61.23),
    'Featherweight': (61.24, 65.77),
    'Lightweight': (65.78, 70.31),
    'Welterweight': (70.32, 77.11),
    'Middleweight': (77.12, 83.91),
    'Light Heavyweight': (83.92, 92.99),
    'Heavyweight': (93.00, 120.20)
}

def get_weight_class(weight):
    """Retorna a categoria de peso do lutador."""
    if pd.isna(weight):
        return 'Unknown'
    for class_name, (min_w, max_w) in WEIGHT_CLASSES.items():
        if min_w <= weight <= max_w:
            return class_name
    return 'Heavyweight'

def weight_classes_compatible(weight1, weight2, max_diff=1):
    """Verifica se os pesos estão em categorias compatíveis (máximo 1 categoria de diferença)."""
    if pd.isna(weight1) or pd.isna(weight2):
        return True
    classes = list(WEIGHT_CLASSES.keys())
    class1 = get_weight_class(weight1)
    class2 = get_weight_class(weight2)
    
    if class1 not in classes or class2 not in classes:
        return True
    
    idx1 = classes.index(class1)
    idx2 = classes.index(class2)
    
    return abs(idx1 - idx2) <= max_diff

def predict_fight(fighter1_name, fighter2_name):
    """Prediz o resultado da luta entre dois lutadores usando o modelo XGBoost calibrado com Elo."""
    f1 = fighters_df[fighters_df['name'].str.contains(fighter1_name, case=False, na=False)]
    f2 = fighters_df[fighters_df['name'].str.contains(fighter2_name, case=False, na=False)]
    
    if f1.empty:
        print(f"Lutador '{fighter1_name}' não encontrado!")
        return None
    if f2.empty:
        print(f"Lutador '{fighter2_name}' não encontrado!")
        return None
    
    f1 = f1.iloc[0]
    f2 = f2.iloc[0]
    
    class1 = get_weight_class(f1['weight'])
    class2 = get_weight_class(f2['weight'])
    
    # Validação de categoria de peso
    if not weight_classes_compatible(f1['weight'], f2['weight']):
        print(f"\n{'='*60}")
        print("AVISO: LUTA INVÁLIDA (DIFERENÇA DE CATEGORIA EXCESSIVA)")
        print(f"{'='*60}")
        print(f"\n{f1['name']} ({f1['weight']:.1f}kg - {class1})")
        print("  vs")
        print(f"{f2['name']} ({f2['weight']:.1f}kg - {class2})")
        print(f"\nA diferença de peso é de {abs(f1['weight'] - f2['weight']):.1f}kg.")
        print("O UFC não permite lutas com mais de 1 divisão de diferença.")
        print(f"{'='*60}\n")
        return None
    
    elo1 = get_fighter_elo(f1['name'], elo_ratings)
    elo2 = get_fighter_elo(f2['name'], elo_ratings)
    strk1 = int(f1.get('streak', 0))
    strk2 = int(f2.get('streak', 0))
    
    # Extrai o vetor de 47 atributos padronizado
    X = extract_matchup_features(f1, f2, elo1, elo2, streak1=strk1, streak2=strk2)
    
    # Predição com modelo calibrado
    prob = model.predict_proba(X)[0] # [P(f2 vence), P(f1 vence)]
    winner_idx = np.argmax(prob)
    winner = f1['name'] if winner_idx == 1 else f2['name']
    confidence = prob[winner_idx] * 100
    
    def format_streak(s):
        if s > 0:
            return f"+{s} vitórias seguidas"
        elif s < 0:
            return f"{abs(s)} derrotas seguidas"
        return "Neutro"

    print(f"\n{'='*60}")
    print("FIGHT PREDICTION - CALIBRATED XGBOOST + ELO MODEL")
    print(f"{'='*60}")
    print(f"\n{f1['name']} ({int(f1['wins'])}-{int(f1['losses'])}-{int(f1.get('draws', 0))}) | Elo: {elo1:.0f} | {format_streak(strk1)} - {class1}")
    print("  vs")
    print(f"{f2['name']} ({int(f2['wins'])}-{int(f2['losses'])}-{int(f2.get('draws', 0))}) | Elo: {elo2:.0f} | {format_streak(strk2)} - {class2}")
    print(f"\n{'-'*60}")
    print(f"PREDICTED WINNER: {winner}")
    print(f"CONFIDENCE: {confidence:.1f}% (Probabilidade Calibrada)")
    print("\nProbabilidades:")
    print(f"  {f1['name']}: {prob[1]*100:.1f}%")
    print(f"  {f2['name']}: {prob[0]*100:.1f}%")
    print(f"{'='*60}\n")
    
    print("ANÁLISE ESTATÍSTICA DO CONFRONTO:")
    
    # Momento
    print(f"\nMomento Competitivo (Sequência):")
    print(f"  {f1['name']}: {format_streak(strk1)}")
    print(f"  {f2['name']}: {format_streak(strk2)}")
    
    # Elo
    print(f"\nRating Elo Histórico:")
    print(f"  {f1['name']}: {elo1:.0f}")
    print(f"  {f2['name']}: {elo2:.0f}")
    print(f"  Diferença de Elo: {abs(elo1 - elo2):.0f} pontos a favor de {f1['name'] if elo1 > elo2 else f2['name']}")
    
    # Físico
    print(f"\nVantagens Físicas:")
    if pd.notna(f1['height']) and pd.notna(f2['height']):
        if f1['height'] > f2['height']:
            print(f"  - {f1['name']} é {f1['height'] - f2['height']:.1f}cm mais alto")
        elif f2['height'] > f1['height']:
            print(f"  - {f2['name']} é {f2['height'] - f1['height']:.1f}cm mais alto")
    
    if pd.notna(f1['reach']) and pd.notna(f2['reach']):
        if f1['reach'] > f2['reach']:
            print(f"  - {f1['name']} tem {f1['reach'] - f2['reach']:.1f}cm de vantagem de envergadura")
        elif f2['reach'] > f1['reach']:
            print(f"  - {f2['name']} tem {f2['reach'] - f1['reach']:.1f}cm de vantagem de envergadura")
    
    # Striking
    print(f"\nEstatísticas de Striking:")
    print(f"  {f1['name']}: {f1['splm']:.2f} golpes/min | {f1['str_acc']:.0f}% precisão | {f1['str_def']:.0f}% defesa")
    print(f"  {f2['name']}: {f2['splm']:.2f} golpes/min | {f2['str_acc']:.0f}% precisão | {f2['str_def']:.0f}% defesa")
    
    # Grappling
    print(f"\nEstatísticas de Grappling:")
    print(f"  {f1['name']}: {f1['td_avg']:.2f} quedas/luta | {f1['td_avg_acc']:.0f}% precisão | {f1['td_def']:.0f}% defesa")
    print(f"  {f2['name']}: {f2['td_avg']:.2f} quedas/luta | {f2['td_avg_acc']:.0f}% precisão | {f2['td_def']:.0f}% defesa")
    print()
    
    return {
        'winner': winner,
        'confidence': confidence,
        'prob_f1': prob[1],
        'prob_f2': prob[0]
    }

def search_fighter(name):
    """Busca lutadores pelo nome e exibe registro e Elo."""
    results = fighters_df[fighters_df['name'].str.contains(name, case=False, na=False)]
    if results.empty:
        print(f"Nenhum lutador encontrado com '{name}'")
    else:
        print(f"\nLutadores encontrados ({len(results)}):")
        for idx, fighter in results.iterrows():
            weight_class = get_weight_class(fighter['weight'])
            elo = get_fighter_elo(fighter['name'], elo_ratings)
            print(f"  - {fighter['name']:<25} ({int(fighter['wins'])}-{int(fighter['losses'])}-{int(fighter.get('draws', 0))}) | Elo: {elo:.0f} | {weight_class}")

if __name__ == "__main__":
    print("="*60)
    print("UFC FIGHT PREDICTION SYSTEM - CALIBRATED XGBOOST + ELO")
    print("="*60)
    
    # Demonstração rápida
    print("\nExecutando teste com Jon Jones vs Stipe Miocic:")
    predict_fight("Jon Jones", "Stipe Miocic")
    
    while True:
        print("\nOpções:")
        print("1 - Prever luta")
        print("2 - Buscar lutador")
        print("3 - Sair")
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
        except EOFError:
            break
            
        if choice == '1':
            fighter1 = input("\nNome do Lutador 1: ").strip()
            fighter2 = input("Nome do Lutador 2: ").strip()
            predict_fight(fighter1, fighter2)
        elif choice == '2':
            name = input("\nNome para busca: ").strip()
            search_fighter(name)
        elif choice == '3':
            print("\nEncerrando...")
            break
        else:
            print("\nOpção inválida!")
