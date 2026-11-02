import pandas as pd
import numpy as np
import os
from data_loader import ensure_data

def calculate_elo_ratings(csv_path=None, k_factor=32, initial_elo=1500):
    """
    Calcula o rating Elo histórico de cada lutador baseado no histórico de confrontos.
    
    Parâmetros:
    -----------
    csv_path : str, opcional
        Caminho para o arquivo CSV com os dados das lutas. Se None, usa data/UFC.csv
    k_factor : int
        Fator K do sistema Elo (padrão: 32)
    initial_elo : int
        Rating Elo inicial para novos lutadores (padrão: 1500)
    
    Retorna:
    --------
    tuple: (elo_ratings_dict, elo_history_df, df_enriched)
        - elo_ratings_dict: Dicionário com o Elo final de cada lutador
        - elo_history_df: DataFrame com o histórico completo de Elo por luta
        - df_enriched: DataFrame das lutas com colunas r_elo_before, b_elo_before, elo_diff
    """
    if csv_path is None:
        csv_path = ensure_data()['ufc']
        
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    df = df.sort_values('date').reset_index(drop=True)
    
    elo_ratings = {}
    elo_history = []
    
    r_elo_before_list = []
    b_elo_before_list = []
    
    for idx, row in df.iterrows():
        r_fighter = row['r_name']
        b_fighter = row['b_name']
        winner = row['winner']
        date = row['date']
        
        # Ratings antes da luta
        r_elo_before = elo_ratings.get(r_fighter, initial_elo)
        b_elo_before = elo_ratings.get(b_fighter, initial_elo)
        
        r_elo_before_list.append(r_elo_before)
        b_elo_before_list.append(b_elo_before)
        
        if pd.isna(r_fighter) or pd.isna(b_fighter) or pd.isna(winner):
            continue
        
        if r_fighter not in elo_ratings:
            elo_ratings[r_fighter] = initial_elo
        if b_fighter not in elo_ratings:
            elo_ratings[b_fighter] = initial_elo
        
        expected_r = 1 / (1 + 10 ** ((b_elo_before - r_elo_before) / 400))
        expected_b = 1 / (1 + 10 ** ((r_elo_before - b_elo_before) / 400))
        
        if winner == r_fighter:
            actual_r, actual_b = 1, 0
        elif winner == b_fighter:
            actual_r, actual_b = 0, 1
        else:
            actual_r, actual_b = 0.5, 0.5
        
        r_elo_after = r_elo_before + k_factor * (actual_r - expected_r)
        b_elo_after = b_elo_before + k_factor * (actual_b - expected_b)
        
        elo_ratings[r_fighter] = r_elo_after
        elo_ratings[b_fighter] = b_elo_after
        
        elo_history.append({
            'date': date,
            'fight_id': row.get('fight_id', idx),
            'r_name': r_fighter,
            'b_name': b_fighter,
            'winner': winner,
            'r_elo_before': r_elo_before,
            'b_elo_before': b_elo_before,
            'r_elo_after': r_elo_after,
            'b_elo_after': b_elo_after,
            'r_elo_change': r_elo_after - r_elo_before,
            'b_elo_change': b_elo_after - b_elo_before
        })
    
    df['r_elo_before'] = r_elo_before_list
    df['b_elo_before'] = b_elo_before_list
    df['elo_diff'] = df['r_elo_before'] - df['b_elo_before']
    df['elo_expected_r'] = 1 / (1 + 10 ** (-df['elo_diff'] / 400))
    
    elo_history_df = pd.DataFrame(elo_history)
    
    return elo_ratings, elo_history_df, df


def get_fighter_elo(fighter_name, elo_ratings):
    """Retorna o Elo atual de um lutador."""
    return elo_ratings.get(fighter_name, 1500)


def get_top_fighters_by_elo(elo_ratings, top_n=20):
    """Retorna os top N lutadores por rating Elo."""
    sorted_fighters = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    return pd.DataFrame(sorted_fighters[:top_n], columns=['Fighter', 'Elo Rating'])


def save_elo_ratings(elo_ratings, elo_history_df, output_dir='data'):
    """Salva os ratings Elo em arquivos CSV."""
    os.makedirs(output_dir, exist_ok=True)
    
    elo_df = pd.DataFrame(list(elo_ratings.items()), columns=['fighter', 'elo_rating'])
    elo_df = elo_df.sort_values('elo_rating', ascending=False).reset_index(drop=True)
    elo_df.to_csv(os.path.join(output_dir, 'fighter_elo_ratings.csv'), index=False)
    
    elo_history_df.to_csv(os.path.join(output_dir, 'elo_history.csv'), index=False)
    
    print(f"Elo ratings salvos em '{os.path.join(output_dir, 'fighter_elo_ratings.csv')}'")
    print(f"Historico Elo salvo em '{os.path.join(output_dir, 'elo_history.csv')}'")


if __name__ == '__main__':
    print("Calculando ratings Elo historicos...")
    elo_ratings, elo_history, _ = calculate_elo_ratings()
    
    print(f"\nCalculo concluido!")
    print(f"Total de lutadores: {len(elo_ratings)}")
    print(f"Total de lutas processadas: {len(elo_history)}")
    
    print("\nTOP 20 LUTADORES POR ELO RATING:")
    print("="*60)
    top_fighters = get_top_fighters_by_elo(elo_ratings, top_n=20)
    for idx, row in top_fighters.iterrows():
        print(f"{idx+1:2d}. {row['Fighter']:30s} - {row['Elo Rating']:.0f}")
    
    save_elo_ratings(elo_ratings, elo_history, output_dir='data')
