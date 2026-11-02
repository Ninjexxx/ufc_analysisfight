import os
import pickle
import numpy as np
import pandas as pd

from data_loader import load_fighters_df
from calculate_elo import calculate_elo_ratings, get_fighter_elo
from feature_engineering import extract_matchup_features

MODEL_PATH = 'ufc_model.pkl'
if not os.path.exists(MODEL_PATH):
    from train_model import train_random_forest
    train_random_forest()

with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

fighters_df = load_fighters_df()

ELO_CSV = os.path.join('data', 'fighter_elo_ratings.csv')
if os.path.exists(ELO_CSV):
    elo_df = pd.read_csv(ELO_CSV)
    elo_ratings = dict(zip(elo_df['fighter'], elo_df['elo_rating']))
else:
    elo_ratings, _, _ = calculate_elo_ratings()

def predict_fight(fighter1_name, fighter2_name):
    """Predição de luta utilizando o modelo Random Forest."""
    f1 = fighters_df[fighters_df['name'].str.contains(fighter1_name, case=False, na=False)]
    f2 = fighters_df[fighters_df['name'].str.contains(fighter2_name, case=False, na=False)]
    
    if f1.empty:
        print(f"Lutador '{fighter1_name}' não encontrado!")
        return
    if f2.empty:
        print(f"Lutador '{fighter2_name}' não encontrado!")
        return
    
    f1 = f1.iloc[0]
    f2 = f2.iloc[0]
    
    elo1 = get_fighter_elo(f1['name'], elo_ratings)
    elo2 = get_fighter_elo(f2['name'], elo_ratings)
    
    X = extract_matchup_features(f1, f2, elo1, elo2)
    
    prob = model.predict_proba(X)[0]
    winner_idx = np.argmax(prob)
    winner = f1['name'] if winner_idx == 1 else f2['name']
    confidence = prob[winner_idx] * 100
    
    print(f"\n{'='*60}")
    print("FIGHT PREDICTION - RANDOM FOREST BASELINE")
    print(f"{'='*60}")
    print(f"\n{f1['name']} ({int(f1['wins'])}-{int(f1['losses'])}-{int(f1.get('draws', 0))}) | Elo: {elo1:.0f}")
    print("  vs")
    print(f"{f2['name']} ({int(f2['wins'])}-{int(f2['losses'])}-{int(f2.get('draws', 0))}) | Elo: {elo2:.0f}")
    print(f"\n{'-'*60}")
    print(f"PREDICTED WINNER: {winner}")
    print(f"CONFIDENCE: {confidence:.1f}%")
    print("\nProbabilities:")
    print(f"  {f1['name']}: {prob[1]*100:.1f}%")
    print(f"  {f2['name']}: {prob[0]*100:.1f}%")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("UFC FIGHT PREDICTION SYSTEM - RANDOM FOREST\n")
    predict_fight("Jon Jones", "Stipe Miocic")
    predict_fight("Islam Makhachev", "Charles Oliveira")
