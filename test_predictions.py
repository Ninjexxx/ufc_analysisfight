import pandas as pd
import pickle
import numpy as np

# Load XGBoost model and data
with open('ufc_xgboost_model.pkl', 'rb') as f:
    model = pickle.load(f)

fighters_df = pd.read_csv(r"C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\fighter_details.csv")

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
    """Returns the fighter's weight class"""
    for class_name, (min_w, max_w) in WEIGHT_CLASSES.items():
        if min_w <= weight <= max_w:
            return class_name
    return 'Heavyweight'

def weight_classes_compatible(weight1, weight2, max_diff=1):
    """Checks if two weights are in compatible categories (max 1 category difference)"""
    classes = list(WEIGHT_CLASSES.keys())
    class1 = get_weight_class(weight1)
    class2 = get_weight_class(weight2)
    
    idx1 = classes.index(class1)
    idx2 = classes.index(class2)
    
    return abs(idx1 - idx2) <= max_diff

def predict_fight(fighter1_name, fighter2_name):
    """Predicts the outcome of a fight between two fighters"""
    
    # Search for fighters
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
    
    # Validate weight class compatibility
    class1 = get_weight_class(f1['weight'])
    class2 = get_weight_class(f2['weight'])
    
    if not weight_classes_compatible(f1['weight'], f2['weight']):
        print(f"\n{'='*60}")
        print(f"WARNING: INVALID FIGHT")
        print(f"{'='*60}")
        print(f"\n{f1['name']} ({f1['weight']:.1f}kg - {class1})")
        print(f"  vs")
        print(f"{f2['name']} ({f2['weight']:.1f}kg - {class2})")
        print(f"\nThis fight is not realistic!")
        print(f"The weight difference is too large: {abs(f1['weight'] - f2['weight']):.1f}kg")
        print(f"\nThe UFC does not allow fights with more than 1 weight class difference.")
        print(f"Choose fighters from the same category or adjacent categories.")
        print(f"{'='*60}\n")
        return
    
    # Calculate win rates
    r_win_rate = f1['wins'] / (f1['wins'] + f1['losses'] + 1)
    b_win_rate = f2['wins'] / (f2['wins'] + f2['losses'] + 1)
    
    # Prepare features (same as training)
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
        'b_td_avg_acc': f2['td_avg_acc'], 'b_td_def': f2['td_def'], 'b_sub_avg': f2['sub_avg'],
        # Engineered features
        'win_diff': f1['wins'] - f2['wins'],
        'loss_diff': f1['losses'] - f2['losses'],
        'height_diff': f1['height'] - f2['height'],
        'reach_diff': f1['reach'] - f2['reach'],
        'weight_diff': f1['weight'] - f2['weight'],
        'r_win_rate': r_win_rate,
        'b_win_rate': b_win_rate,
        'win_rate_diff': r_win_rate - b_win_rate,
        'str_acc_diff': f1['str_acc'] - f2['str_acc'],
        'str_def_diff': f1['str_def'] - f2['str_def'],
        'td_avg_diff': f1['td_avg'] - f2['td_avg'],
        'td_def_diff': f1['td_def'] - f2['td_def'],
        'splm_diff': f1['splm'] - f2['splm'],
        'sapm_diff': f1['sapm'] - f2['sapm']
    }
    
    X = pd.DataFrame([features])
    
    # Prediction
    prob = model.predict_proba(X)[0]
    winner_idx = np.argmax(prob)
    winner = f1['name'] if winner_idx == 1 else f2['name']
    confidence = prob[winner_idx] * 100
    
    # Display result
    print(f"\n{'='*60}")
    print(f"FIGHT PREDICTION - XGBOOST MODEL")
    print(f"{'='*60}")
    print(f"\n{f1['name']} ({f1['wins']}-{f1['losses']}-{f1['draws']}) - {class1}")
    print(f"  vs")
    print(f"{f2['name']} ({f2['wins']}-{f2['losses']}-{f2['draws']}) - {class2}")
    print(f"\n{'-'*60}")
    print(f"PREDICTED WINNER: {winner}")
    print(f"CONFIDENCE: {confidence:.1f}%")
    print(f"\nProbabilities:")
    print(f"  {f1['name']}: {prob[1]*100:.1f}%")
    print(f"  {f2['name']}: {prob[0]*100:.1f}%")
    print(f"{'='*60}\n")
    
    # Matchup analysis
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
    
    print(f"\nWin rate:")
    print(f"  {f1['name']}: {r_win_rate*100:.1f}%")
    print(f"  {f2['name']}: {b_win_rate*100:.1f}%")
    
    print(f"\nStriking statistics:")
    print(f"  {f1['name']}: {f1['splm']:.2f} strikes/min | {f1['str_acc']}% accuracy | {f1['str_def']}% defense")
    print(f"  {f2['name']}: {f2['splm']:.2f} strikes/min | {f2['str_acc']}% accuracy | {f2['str_def']}% defense")
    
    print(f"\nGrappling statistics:")
    print(f"  {f1['name']}: {f1['td_avg']:.2f} TD/fight | {f1['td_avg_acc']}% accuracy | {f1['td_def']}% defense")
    print(f"  {f2['name']}: {f2['td_avg']:.2f} TD/fight | {f2['td_avg_acc']}% accuracy | {f2['td_def']}% defense")
    print()

def search_fighter(name):
    """Search for fighters by name"""
    results = fighters_df[fighters_df['name'].str.contains(name, case=False, na=False)]
    if results.empty:
        print(f"No fighter found with '{name}'")
    else:
        print(f"\nFighters found ({len(results)}):")
        for idx, fighter in results.iterrows():
            weight_class = get_weight_class(fighter['weight'])
            print(f"  - {fighter['name']} ({fighter['wins']}-{fighter['losses']}-{fighter['draws']}) - {weight_class}")

# Interactive menu
if __name__ == "__main__":
    print("="*60)
    print("UFC FIGHT PREDICTION SYSTEM - XGBOOST")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1 - Predict fight")
        print("2 - Search fighter")
        print("3 - Exit")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == '1':
            fighter1 = input("\nFighter 1 name: ").strip()
            fighter2 = input("Fighter 2 name: ").strip()
            predict_fight(fighter1, fighter2)
        
        elif choice == '2':
            name = input("\nFighter name: ").strip()
            search_fighter(name)
        
        elif choice == '3':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid option!")
