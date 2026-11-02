import os
import shutil
import re
import pandas as pd
import numpy as np

KAGGLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ufcdataset_kaggle')
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def parse_height(h):
    if pd.isna(h):
        return np.nan
    if isinstance(h, (int, float)):
        return float(h)
    m = re.match(r'(\d+)\s*\'\s*(\d+)?', str(h))
    if m:
        feet = int(m.group(1))
        inches = int(m.group(2)) if m.group(2) else 0
        return round(feet * 30.48 + inches * 2.54, 2)
    return np.nan

def parse_val(v, mult):
    try:
        val = float(v)
        return round(val * mult, 2)
    except:
        return np.nan

def get_winner(row):
    if row['result_status'] == 'win':
        if row['winner_id'] == row['r_fighter_id']:
            return row['r_fighter_name']
        elif row['winner_id'] == row['b_fighter_id']:
            return row['b_fighter_name']
    elif row['result_status'] == 'draw':
        return 'Draw'
    elif row['result_status'] == 'no_contest':
        return 'NC'
    return None

def process_kaggle_2026(kaggle_dir=KAGGLE_DIR, output_dir=DATA_DIR):
    """
    Processa os arquivos master.csv e fighter.csv do Kaggle (atualizados até 2026),
    padroniza unidades (cm/kg), calcula registros pré-luta dinâmicos sem vazamento temporal
    e atualiza data/UFC.csv e data/fighter_details.csv.
    """
    master_path = os.path.join(kaggle_dir, 'master.csv')
    fighter_path = os.path.join(kaggle_dir, 'fighter.csv')
    
    if not os.path.exists(master_path) or not os.path.exists(fighter_path):
        raise FileNotFoundError(f"Arquivos master.csv ou fighter.csv não encontrados em {kaggle_dir}")
        
    print(f"Carregando dados de {kaggle_dir}...")
    master = pd.read_csv(master_path)
    fighter = pd.read_csv(fighter_path)
    
    print(f"Total de lutas brutas no master.csv: {len(master)}")
    print(f"Total de lutadores no fighter.csv: {len(fighter)}")
    
    # 1. Ordenação cronológica e mapeamento de vencedores
    master['date'] = pd.to_datetime(master['event_date'])
    master = master.sort_values('date').reset_index(drop=True)
    master['winner'] = master.apply(get_winner, axis=1)
    
    # 2. Cálculo dos registros pré-luta dinâmicos (Wins/Losses e Streaks sequenciais sem vazamento)
    f_wins, f_losses, f_draws = {}, {}, {}
    f_streaks = {}
    r_w, r_l, b_w, b_l = [], [], [], []
    r_streaks, b_streaks = [], []
    
    for idx, row in master.iterrows():
        rf = row['r_fighter_name']
        bf = row['b_fighter_name']
        
        rw = f_wins.get(rf, 0)
        rl = f_losses.get(rf, 0)
        bw = f_wins.get(bf, 0)
        bl = f_losses.get(bf, 0)
        
        rs = f_streaks.get(rf, 0)
        bs = f_streaks.get(bf, 0)
        
        r_w.append(rw)
        r_l.append(rl)
        b_w.append(bw)
        b_l.append(bl)
        
        r_streaks.append(rs)
        b_streaks.append(bs)
        
        w = row['winner']
        if w == rf:
            f_wins[rf] = rw + 1
            f_losses[bf] = bl + 1
            f_streaks[rf] = rs + 1 if rs > 0 else 1
            f_streaks[bf] = bs - 1 if bs < 0 else -1
        elif w == bf:
            f_wins[bf] = bw + 1
            f_losses[rf] = rl + 1
            f_streaks[bf] = bs + 1 if bs > 0 else 1
            f_streaks[rf] = rs - 1 if rs < 0 else -1
        elif w == 'Draw':
            f_draws[rf] = f_draws.get(rf, 0) + 1
            f_draws[bf] = f_draws.get(bf, 0) + 1

    master['r_wins'] = r_w
    master['r_losses'] = r_l
    master['b_wins'] = b_w
    master['b_losses'] = b_l
    master['r_streak'] = r_streaks
    master['b_streak'] = b_streaks
    master['streak_diff'] = master['r_streak'] - master['b_streak']
    
    # 3. Conversão de Unidades e Nomes de Colunas para UFC.csv
    master['r_height'] = master['r_height'].apply(parse_height)
    master['b_height'] = master['b_height'].apply(parse_height)
    master['r_weight'] = master['r_weight_lbs'].apply(lambda w: parse_val(w, 0.45359237))
    master['b_weight'] = master['b_weight_lbs'].apply(lambda w: parse_val(w, 0.45359237))
    master['r_reach'] = master['r_reach_inches'].apply(lambda r: parse_val(r, 2.54))
    master['b_reach'] = master['b_reach_inches'].apply(lambda r: parse_val(r, 2.54))
    
    master['r_name'] = master['r_fighter_name']
    master['b_name'] = master['b_fighter_name']
    master['r_splm'] = master['r_slpm']
    master['b_splm'] = master['b_slpm']
    master['r_td_avg_acc'] = master['r_td_acc']
    master['b_td_avg_acc'] = master['b_td_acc']
    master['division'] = master['weight_class']
    
    # Formato de data em string compatível: YYYY/MM/DD
    master['date'] = master['date'].dt.strftime('%Y/%m/%d')
    
    # 4. Processamento de fighter_details.csv
    fighter['height'] = fighter['height'].apply(parse_height)
    fighter['weight'] = fighter['weight_lbs'].apply(lambda w: parse_val(w, 0.45359237))
    fighter['reach'] = fighter['reach_inches'].apply(lambda r: parse_val(r, 2.54))
    fighter['splm'] = fighter['slpm']
    fighter['td_avg_acc'] = fighter['td_acc']
    fighter['id'] = fighter['fighter_id']
    fighter['name'] = fighter['fighter_name']
    fighter['nick_name'] = fighter['fighter_nick_name']
    fighter['wins'] = fighter['fighter_name'].map(f_wins).fillna(0).astype(int)
    fighter['losses'] = fighter['fighter_name'].map(f_losses).fillna(0).astype(int)
    fighter['draws'] = fighter['fighter_name'].map(f_draws).fillna(0).astype(int)
    fighter['streak'] = fighter['fighter_name'].map(f_streaks).fillna(0).astype(int)
    
    # 5. Backup e Salvamento
    os.makedirs(output_dir, exist_ok=True)
    target_ufc = os.path.join(output_dir, 'UFC.csv')
    target_fighter = os.path.join(output_dir, 'fighter_details.csv')
    
    if os.path.exists(target_ufc):
        backup_ufc = os.path.join(output_dir, 'UFC_2025_backup.csv')
        if not os.path.exists(backup_ufc):
            shutil.copy2(target_ufc, backup_ufc)
            print(f"Backup do UFC.csv anterior salvo em {backup_ufc}")
            
    master.to_csv(target_ufc, index=False)
    fighter.to_csv(target_fighter, index=False)
    
    print("\n" + "="*60)
    print("ATUALIZAÇÃO DE DADOS 2026 CONCLUÍDA")
    print("="*60)
    print(f"Salvo em '{target_ufc}' ({len(master)} lutas, 1993 a 2026)")
    print(f"Salvo em '{target_fighter}' ({len(fighter)} lutadores)")
    return master, fighter

if __name__ == '__main__':
    process_kaggle_2026()
