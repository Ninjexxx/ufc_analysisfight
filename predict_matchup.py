import pandas as pd
import pickle
import numpy as np

with open('ufc_model.pkl', 'rb') as f:
    model = pickle.load(f)

fighters_df = pd.read_csv(r"C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\fighter_details.csv")

def predict_fight(fighter1_name, fighter2_name):
    """Predicts the outcome of a fight between two fighters"""
    
    f1 = fighters_df[fighters_df['name'].str.contains(fighter1_name, case=False, na=False)]
    f2 = fighters_df[fighters_df['name'].str.contains(fighter2_name, case=False, na=False)]
    
    if f1.empty:
        print(f"Fighter '{fighter1_name}' not found!")
        return
    if f2.empty:
        print(f"Fighter '{fighter2_name}' not found!")
        return
    
    f1 = f1.iloc[0]
    f2 = f2.iloc[0]
    
    features = {
        'r_wins': f1['wins'], 'r_losses': f1['losses'],
        'r_height': f1['height'], 'r_weight': f1['weight'], 'r_reach': f1['reach'],
        'r_splm': f1['splm'], 'r_str_acc': f1['str_acc'], 'r_sapm': f1['sapm'],
        'r_str_def': f1['str_def'], 'r_td_avg': f1['td_avg'],
        'r_td_avg_acc': f1['td_avg_acc'], 'r_td_def': f1['td_def'], 'r_sub_avg': f1['sub_avg'],
        'b_wins': f2['wins'], 'b_losses': f2['losses'],
        'b_height': f2['height'], 'b_weight': f2['weight'], 'b_reach': f2['reach'],
        'b_splm': f2['splm'], 'b_str_acc': f2['str_acc'], 'b_sapm': f2['sapm'],
        'b_str_def': f2['str_def'], 'b_td_avg': f2['td_avg'],
        'b_td_avg_acc': f2['td_avg_acc'], 'b_td_def': f2['td_def'], 'b_sub_avg': f2['sub_avg']
    }
    
    X = pd.DataFrame([features])
    
    prob = model.predict_proba(X)[0]
    winner_idx = np.argmax(prob)
    winner = f1['name'] if winner_idx == 1 else f2['name']
    confidence = prob[winner_idx] * 100
    
    print(f"\n{'='*60}")
    print(f"FIGHT PREDICTION")
    print(f"{'='*60}")
    print(f"\n{f1['name']} ({f1['wins']}-{f1['losses']}-{f1['draws']})")
    print(f"  vs")
    print(f"{f2['name']} ({f2['wins']}-{f2['losses']}-{f2['draws']})")
    print(f"\n{'-'*60}")
    print(f"PREDICTED WINNER: {winner}")
    print(f"CONFIDENCE: {confidence:.1f}%")
    print(f"\nProbabilities:")
    print(f"  {f1['name']}: {prob[1]*100:.1f}%")
    print(f"  {f2['name']}: {prob[0]*100:.1f}%")
    print(f"{'='*60}\n")
    
    print("MATCHUP ANALYSIS:")
    print(f"\nPhysical advantages:")
    if f1['height'] > f2['height']:
        print(f"  - {f1['name']} is {f1['height'] - f2['height']:.1f}cm taller")
    elif f2['height'] > f1['height']:
        print(f"  - {f2['name']} is {f2['height'] - f1['height']:.1f}cm taller")
    
    if f1['reach'] > f2['reach']:
        print(f"  - {f1['name']} has {f1['reach'] - f2['reach']:.1f}cm more reach")
    elif f2['reach'] > f1['reach']:
        print(f"  - {f2['name']} has {f2['reach'] - f1['reach']:.1f}cm more reach")
    
    print(f"\nStriking statistics:")
    print(f"  {f1['name']}: {f1['splm']:.2f} strikes/min | {f1['str_acc']}% accuracy | {f1['str_def']}% defense")
    print(f"  {f2['name']}: {f2['splm']:.2f} strikes/min | {f2['str_acc']}% accuracy | {f2['str_def']}% defense")
    
    print(f"\nGrappling statistics:")
    print(f"  {f1['name']}: {f1['td_avg']:.2f} TD/fight | {f1['td_avg_acc']}% accuracy | {f1['td_def']}% defense")
    print(f"  {f2['name']}: {f2['td_avg']:.2f} TD/fight | {f2['td_avg_acc']}% accuracy | {f2['td_def']}% defense")

if __name__ == "__main__":
    print("UFC FIGHT PREDICTION SYSTEM\n")
    
    predict_fight("Jon Jones", "Stipe Miocic")
    predict_fight("Islam Makhachev", "Charles Oliveira")
