import os
import sys
import pickle
import pandas as pd
import numpy as np

def test_files_exist():
    """Tests if required files exist"""
    print("\n" + "="*60)
    print("TEST 1: Checking required files")
    print("="*60)
    
    files = {
        'ufc_xgboost_model.pkl': 'XGBoost Model',
        r'C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\fighter_details.csv': 'Fighters Dataset',
        r'C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\UFC.csv': 'Fights Dataset'
    }
    
    all_exist = True
    for file, desc in files.items():
        exists = os.path.exists(file)
        status = "✓ OK" if exists else "✗ MISSING"
        print(f"{status} - {desc}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Tests model loading"""
    print("\n" + "="*60)
    print("TEST 2: Loading model")
    print("="*60)
    
    try:
        with open('ufc_xgboost_model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✓ Model loaded successfully")
        print(f"  Type: {type(model).__name__}")
        return True, model
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False, None

def test_data_loading():
    """Tests data loading"""
    print("\n" + "="*60)
    print("TEST 3: Loading data")
    print("="*60)
    
    try:
        fighters_df = pd.read_csv(r"C:\Users\Arthur Santos\.cache\kagglehub\datasets\neelagiriaditya\ufc-datasets-1994-2025\versions\3\fighter_details.csv")
        print(f"✓ Dataset loaded: {len(fighters_df)} fighters")
        print(f"  Columns: {list(fighters_df.columns[:5])}...")
        return True, fighters_df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False, None

def test_predictions(model, fighters_df):
    """Tests predictions with known fighters"""
    print("\n" + "="*60)
    print("TEST 4: Testing predictions")
    print("="*60)
    
    test_cases = [
        ("Jon Jones", "Stipe Miocic"),
        ("Islam Makhachev", "Charles Oliveira"),
        ("Alex Pereira", "Israel Adesanya")
    ]
    
    success_count = 0
    for f1_name, f2_name in test_cases:
        try:
            f1 = fighters_df[fighters_df['name'].str.contains(f1_name, case=False, na=False)]
            f2 = fighters_df[fighters_df['name'].str.contains(f2_name, case=False, na=False)]
            
            if f1.empty or f2.empty:
                print(f"⚠ Fighter not found: {f1_name} vs {f2_name}")
                continue
            
            f1 = f1.iloc[0]
            f2 = f2.iloc[0]
            
            r_win_rate = f1['wins'] / (f1['wins'] + f1['losses'] + 1)
            b_win_rate = f2['wins'] / (f2['wins'] + f2['losses'] + 1)
            
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
            prob = model.predict_proba(X)[0]
            winner_idx = np.argmax(prob)
            winner = f1['name'] if winner_idx == 1 else f2['name']
            confidence = prob[winner_idx] * 100
            
            print(f"✓ {f1['name']} vs {f2['name']}")
            print(f"  Winner: {winner} ({confidence:.1f}%)")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error in prediction {f1_name} vs {f2_name}: {e}")
    
    return success_count == len(test_cases)

def test_weight_validation():
    """Tests weight class validation"""
    print("\n" + "="*60)
    print("TEST 6: Weight class validation")
    print("="*60)
    
    import sys
    sys.path.insert(0, r'c:\Users\Arthur Santos\ufc_analysis')
    from test_predictions import get_weight_class, weight_classes_compatible
    
    print("✓ Featherweight (65kg):", get_weight_class(65.0))
    print("✓ Light Heavyweight (93kg):", get_weight_class(93.0))
    
    compatible = weight_classes_compatible(70.31, 77.11)
    print(f"✓ Lightweight vs Welterweight: {'Compatible' if compatible else 'Incompatible'}")
    
    incompatible = weight_classes_compatible(70.31, 92.99)
    print(f"✓ Lightweight vs Light Heavyweight: {'Compatible' if incompatible else 'Incompatible'}")
    
    return True

def test_search_functionality(fighters_df):
    """Tests search functionality"""
    print("\n" + "="*60)
    print("TEST 5: Testing fighter search")
    print("="*60)
    
    searches = ["Jones", "Silva", "McGregor"]
    
    for name in searches:
        results = fighters_df[fighters_df['name'].str.contains(name, case=False, na=False)]
        print(f"✓ Search '{name}': {len(results)} results")
        if len(results) > 0:
            print(f"  Example: {results.iloc[0]['name']}")
    
    return True

def main():
    print("\n" + "="*60)
    print("TEST SUITE - UFC ANALYSIS")
    print("="*60)
    
    results = []
    
    results.append(("Required files", test_files_exist()))
    
    model_ok, model = test_model_loading()
    results.append(("Model loading", model_ok))
    
    data_ok, fighters_df = test_data_loading()
    results.append(("Data loading", data_ok))
    
    if model_ok and data_ok:
        results.append(("Predictions", test_predictions(model, fighters_df)))
        results.append(("Fighter search", test_search_functionality(fighters_df)))
        results.append(("Weight class validation", test_weight_validation()))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Application is working correctly.")
    else:
        print("\n⚠ Some tests failed. Check errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
