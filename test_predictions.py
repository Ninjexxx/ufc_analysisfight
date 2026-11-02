import os
import sys
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
    print("Model 'ufc_xgboost_model.pkl' not found. Training automatically...")
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
    """Returns the fighter's official UFC weight class."""
    if pd.isna(weight):
        return 'Unknown'
    for class_name, (min_w, max_w) in WEIGHT_CLASSES.items():
        if min_w <= weight <= max_w:
            return class_name
    return 'Heavyweight'

def weight_classes_compatible(weight1, weight2, max_diff=1):
    """Checks if two weights are in compatible divisions (maximum 1 division difference)."""
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

def predict_fight(fighter1_name, fighter2_name, lang='en'):
    """
    Predicts the outcome of a fight between two fighters using calibrated XGBoost + Elo.
    Supports English ('en') and Portuguese ('pt').
    """
    f1 = fighters_df[fighters_df['name'].str.contains(fighter1_name, case=False, na=False)]
    f2 = fighters_df[fighters_df['name'].str.contains(fighter2_name, case=False, na=False)]
    
    is_pt = (lang == 'pt')
    
    if f1.empty:
        msg = f"Lutador '{fighter1_name}' não encontrado!" if is_pt else f"Fighter '{fighter1_name}' not found!"
        print(msg)
        return None
    if f2.empty:
        msg = f"Lutador '{fighter2_name}' não encontrado!" if is_pt else f"Fighter '{fighter2_name}' not found!"
        print(msg)
        return None
    
    f1 = f1.iloc[0]
    f2 = f2.iloc[0]
    
    class1 = get_weight_class(f1['weight'])
    class2 = get_weight_class(f2['weight'])
    
    # Weight class validation
    if not weight_classes_compatible(f1['weight'], f2['weight']):
        print(f"\n{'='*60}")
        header = "AVISO: LUTA INVÁLIDA (DIFERENÇA DE CATEGORIA)" if is_pt else "WARNING: INVALID FIGHT (WEIGHT CLASS DIFFERENCE TOO LARGE)"
        print(header)
        print(f"{'='*60}")
        print(f"\n{f1['name']} ({f1['weight']:.1f}kg - {class1})")
        print("  vs")
        print(f"{f2['name']} ({f2['weight']:.1f}kg - {class2})")
        diff = abs(f1['weight'] - f2['weight'])
        if is_pt:
            print(f"\nA diferença de peso é de {diff:.1f}kg.")
            print("O UFC não permite lutas com mais de 1 divisão de diferença.")
        else:
            print(f"\nThe weight difference is {diff:.1f}kg.")
            print("The UFC does not permit fights with more than 1 division difference.")
        print(f"{'='*60}\n")
        return None
    
    elo1 = get_fighter_elo(f1['name'], elo_ratings)
    elo2 = get_fighter_elo(f2['name'], elo_ratings)
    strk1 = int(f1.get('streak', 0))
    strk2 = int(f2.get('streak', 0))
    
    # Vector of 47 features
    X = extract_matchup_features(f1, f2, elo1, elo2, streak1=strk1, streak2=strk2)
    
    prob = model.predict_proba(X)[0]
    winner_idx = np.argmax(prob)
    winner = f1['name'] if winner_idx == 1 else f2['name']
    confidence = prob[winner_idx] * 100
    
    def format_streak(s):
        if is_pt:
            if s > 0:
                return f"+{s} vitórias seguidas"
            elif s < 0:
                return f"{abs(s)} derrotas seguidas"
            return "Neutro"
        else:
            if s > 0:
                return f"+{s} win streak"
            elif s < 0:
                return f"{abs(s)} loss streak"
            return "Neutral"

    print(f"\n{'='*60}")
    title = "FIGHT PREDICTION - CALIBRATED XGBOOST + ELO MODEL" if not is_pt else "PREVISÃO DE LUTA - MODELO XGBOOST CALIBRADO + ELO"
    print(title)
    print(f"{'='*60}")
    print(f"\n{f1['name']} ({int(f1['wins'])}-{int(f1['losses'])}-{int(f1.get('draws', 0))}) | Elo: {elo1:.0f} | {format_streak(strk1)} - {class1}")
    print("  vs")
    print(f"{f2['name']} ({int(f2['wins'])}-{int(f2['losses'])}-{int(f2.get('draws', 0))}) | Elo: {elo2:.0f} | {format_streak(strk2)} - {class2}")
    print(f"\n{'-'*60}")
    win_label = "PREDICTED WINNER" if not is_pt else "VENCEDOR PREVISTO"
    conf_label = "CONFIDENCE (Calibrated Probability)" if not is_pt else "CONFIANÇA (Probabilidade Calibrada)"
    print(f"{win_label}: {winner}")
    print(f"{conf_label}: {confidence:.1f}%")
    print(f"\n{'Probabilities' if not is_pt else 'Probabilidades'}:")
    print(f"  {f1['name']}: {prob[1]*100:.1f}%")
    print(f"  {f2['name']}: {prob[0]*100:.1f}%")
    print(f"{'='*60}\n")
    
    print("MATCHUP STATISTICAL ANALYSIS:" if not is_pt else "ANÁLISE ESTATÍSTICA DO CONFRONTO:")
    
    # Momentum
    print(f"\n{'Competitive Momentum (Streak)' if not is_pt else 'Momento Competitivo (Sequência)'}:")
    print(f"  {f1['name']}: {format_streak(strk1)}")
    print(f"  {f2['name']}: {format_streak(strk2)}")
    
    # Elo
    print(f"\n{'Historical Elo Rating' if not is_pt else 'Rating Elo Histórico'}:")
    print(f"  {f1['name']}: {elo1:.0f}")
    print(f"  {f2['name']}: {elo2:.0f}")
    leader = f1['name'] if elo1 > elo2 else f2['name']
    elo_msg = f"  Elo Difference: {abs(elo1 - elo2):.0f} points in favor of {leader}" if not is_pt else f"  Diferença de Elo: {abs(elo1 - elo2):.0f} pontos a favor de {leader}"
    print(elo_msg)
    
    # Physical
    print(f"\n{'Physical Advantages' if not is_pt else 'Vantagens Físicas'}:")
    if pd.notna(f1['height']) and pd.notna(f2['height']):
        if f1['height'] > f2['height']:
            h_msg = f"  - {f1['name']} is {f1['height'] - f2['height']:.1f}cm taller" if not is_pt else f"  - {f1['name']} é {f1['height'] - f2['height']:.1f}cm mais alto"
            print(h_msg)
        elif f2['height'] > f1['height']:
            h_msg = f"  - {f2['name']} is {f2['height'] - f1['height']:.1f}cm taller" if not is_pt else f"  - {f2['name']} é {f2['height'] - f1['height']:.1f}cm mais alto"
            print(h_msg)
    
    if pd.notna(f1['reach']) and pd.notna(f2['reach']):
        if f1['reach'] > f2['reach']:
            r_msg = f"  - {f1['name']} has {f1['reach'] - f2['reach']:.1f}cm reach advantage" if not is_pt else f"  - {f1['name']} tem {f1['reach'] - f2['reach']:.1f}cm de vantagem de envergadura"
            print(r_msg)
        elif f2['reach'] > f1['reach']:
            r_msg = f"  - {f2['name']} has {f2['reach'] - f1['reach']:.1f}cm reach advantage" if not is_pt else f"  - {f2['name']} tem {f2['reach'] - f1['reach']:.1f}cm de vantagem de envergadura"
            print(r_msg)
    
    # Striking
    print(f"\n{'Striking Statistics' if not is_pt else 'Estatísticas de Striking'}:")
    str_unit = "strikes/min" if not is_pt else "golpes/min"
    acc_unit = "acc" if not is_pt else "precisão"
    def_unit = "def" if not is_pt else "defesa"
    print(f"  {f1['name']}: {f1['splm']:.2f} {str_unit} | {f1['str_acc']:.0f}% {acc_unit} | {f1['str_def']:.0f}% {def_unit}")
    print(f"  {f2['name']}: {f2['splm']:.2f} {str_unit} | {f2['str_acc']:.0f}% {acc_unit} | {f2['str_def']:.0f}% {def_unit}")
    
    # Grappling
    print(f"\n{'Grappling Statistics' if not is_pt else 'Estatísticas de Grappling'}:")
    td_unit = "TD/fight" if not is_pt else "quedas/luta"
    print(f"  {f1['name']}: {f1['td_avg']:.2f} {td_unit} | {f1['td_avg_acc']:.0f}% {acc_unit} | {f1['td_def']:.0f}% {def_unit}")
    print(f"  {f2['name']}: {f2['td_avg']:.2f} {td_unit} | {f2['td_avg_acc']:.0f}% {acc_unit} | {f2['td_def']:.0f}% {def_unit}")
    print()
    
    return {
        'winner': winner,
        'confidence': confidence,
        'prob_f1': prob[1],
        'prob_f2': prob[0]
    }

def search_fighter(name, lang='en'):
    """Searches fighters by name and displays record, Elo, and division."""
    results = fighters_df[fighters_df['name'].str.contains(name, case=False, na=False)]
    is_pt = (lang == 'pt')
    if results.empty:
        print(f"Nenhum lutador encontrado com '{name}'" if is_pt else f"No fighter found matching '{name}'")
    else:
        print(f"\n{'Lutadores encontrados' if is_pt else 'Fighters found'} ({len(results)}):")
        for idx, fighter in results.iterrows():
            weight_class = get_weight_class(fighter['weight'])
            elo = get_fighter_elo(fighter['name'], elo_ratings)
            strk = int(fighter.get('streak', 0))
            strk_txt = f"+{strk}W" if strk > 0 else (f"{abs(strk)}L" if strk < 0 else "0")
            print(f"  - {fighter['name']:<25} ({int(fighter['wins'])}-{int(fighter['losses'])}-{int(fighter.get('draws', 0))}) | Elo: {elo:.0f} | Streak: {strk_txt} | {weight_class}")

if __name__ == "__main__":
    lang = 'en'
    if '--pt' in sys.argv or '--lang=pt' in sys.argv:
        lang = 'pt'
    elif '--en' in sys.argv or '--lang=en' in sys.argv:
        lang = 'en'
        
    is_pt = (lang == 'pt')
    print("="*60)
    print("UFC FIGHT PREDICTION SYSTEM - CALIBRATED XGBOOST + ELO" if not is_pt else "PREVISÃO DE LUTAS UFC - XGBOOST CALIBRADO + ELO")
    print("="*60)
    
    # Quick initial demo
    demo_msg = "Running quick demo test (Jon Jones vs Stipe Miocic):" if not is_pt else "Executando teste com Jon Jones vs Stipe Miocic:"
    print(f"\n{demo_msg}")
    predict_fight("Jon Jones", "Stipe Miocic", lang=lang)
    
    while True:
        if is_pt:
            print("\nOpções:")
            print("1 - Prever luta")
            print("2 - Buscar lutador")
            print("3 - Alternar idioma (Switch to English)")
            print("4 - Sair")
            prompt = "\nEscolha uma opção: "
        else:
            print("\nOptions:")
            print("1 - Predict fight")
            print("2 - Search fighter")
            print("3 - Switch language (Mudar para Português)")
            print("4 - Exit")
            prompt = "\nChoose an option: "
            
        try:
            choice = input(prompt).strip()
        except EOFError:
            break
            
        if choice == '1':
            f1_prompt = "\nNome do Lutador 1: " if is_pt else "\nFighter 1 name: "
            f2_prompt = "Nome do Lutador 2: " if is_pt else "Fighter 2 name: "
            fighter1 = input(f1_prompt).strip()
            fighter2 = input(f2_prompt).strip()
            predict_fight(fighter1, fighter2, lang=lang)
        elif choice == '2':
            s_prompt = "\nNome para busca: " if is_pt else "\nSearch fighter name: "
            name = input(s_prompt).strip()
            search_fighter(name, lang=lang)
        elif choice == '3':
            lang = 'en' if is_pt else 'pt'
            is_pt = (lang == 'pt')
            print(f"\nIdioma alterado para: {'Português' if is_pt else 'English'}")
        elif choice == '4':
            print("\nEncerrando..." if is_pt else "\nGoodbye!")
            break
        else:
            print("\nOpção inválida!" if is_pt else "\nInvalid option!")
