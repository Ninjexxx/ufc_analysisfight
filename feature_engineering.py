import pandas as pd
import numpy as np

# Lista padronizada de 47 features utilizadas pelo modelo (incluindo momentum/streak)
FEATURE_COLS = [
    # Métricas Elo (estatística sequencial de habilidade)
    'r_elo_before', 'b_elo_before', 'elo_diff', 'elo_expected_r',
    # Atributos físicos e carreira
    'r_wins', 'r_losses', 'r_height', 'r_weight', 'r_reach',
    'r_splm', 'r_str_acc', 'r_sapm', 'r_str_def', 
    'r_td_avg', 'r_td_avg_acc', 'r_td_def', 'r_sub_avg',
    'b_wins', 'b_losses', 'b_height', 'b_weight', 'b_reach',
    'b_splm', 'b_str_acc', 'b_sapm', 'b_str_def',
    'b_td_avg', 'b_td_avg_acc', 'b_td_def', 'b_sub_avg',
    # Diferenciais relativos
    'win_diff', 'loss_diff', 'height_diff', 'reach_diff', 'weight_diff',
    'r_win_rate', 'b_win_rate', 'win_rate_diff',
    'str_acc_diff', 'str_def_diff', 'td_avg_diff', 'td_def_diff',
    'splm_diff', 'sapm_diff',
    # Momento competitivo (Sequência atual de vitórias/derrotas)
    'r_streak', 'b_streak', 'streak_diff'
]


def extract_matchup_features(f1, f2, elo1=1500, elo2=1500, streak1=None, streak2=None):
    """
    Gera o vetor de atributos comparativo para dois lutadores (f1 vs f2).
    
    Parâmetros:
    -----------
    f1, f2 : dict ou pd.Series com os atributos dos lutadores
    elo1, elo2 : float com os ratings Elo atuais
    streak1, streak2 : int com a sequência atual (se None, busca em f1/f2)
    """
    r_win_rate = f1['wins'] / (f1['wins'] + f1['losses'] + 1)
    b_win_rate = f2['wins'] / (f2['wins'] + f2['losses'] + 1)
    elo_diff = elo1 - elo2
    elo_expected_r = 1 / (1 + 10 ** (-elo_diff / 400))

    r_strk = streak1 if streak1 is not None else f1.get('streak', 0)
    b_strk = streak2 if streak2 is not None else f2.get('streak', 0)
    if pd.isna(r_strk):
        r_strk = 0
    if pd.isna(b_strk):
        b_strk = 0
    streak_diff = r_strk - b_strk

    features = {
        'r_elo_before': elo1,
        'b_elo_before': elo2,
        'elo_diff': elo_diff,
        'elo_expected_r': elo_expected_r,
        'r_wins': f1['wins'],
        'r_losses': f1['losses'],
        'r_height': f1['height'],
        'r_weight': f1['weight'],
        'r_reach': f1['reach'],
        'r_splm': f1['splm'],
        'r_str_acc': f1['str_acc'],
        'r_sapm': f1['sapm'],
        'r_str_def': f1['str_def'],
        'r_td_avg': f1['td_avg'],
        'r_td_avg_acc': f1['td_avg_acc'],
        'r_td_def': f1['td_def'],
        'r_sub_avg': f1['sub_avg'],
        'b_wins': f2['wins'],
        'b_losses': f2['losses'],
        'b_height': f2['height'],
        'b_weight': f2['weight'],
        'b_reach': f2['reach'],
        'b_splm': f2['splm'],
        'b_str_acc': f2['str_acc'],
        'b_sapm': f2['sapm'],
        'b_str_def': f2['str_def'],
        'b_td_avg': f2['td_avg'],
        'b_td_avg_acc': f2['td_avg_acc'],
        'b_td_def': f2['td_def'],
        'b_sub_avg': f2['sub_avg'],
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
        'sapm_diff': f1['sapm'] - f2['sapm'],
        'r_streak': r_strk,
        'b_streak': b_strk,
        'streak_diff': streak_diff
    }

    return pd.DataFrame([features])[FEATURE_COLS]


def build_training_features(df):
    """
    Calcula as features de diferença para o DataFrame histórico.
    """
    df = df.copy()
    df['r_win'] = (df['winner'] == df['r_name']).astype(int)

    df['win_diff'] = df['r_wins'] - df['b_wins']
    df['loss_diff'] = df['r_losses'] - df['b_losses']
    df['height_diff'] = df['r_height'] - df['b_height']
    df['reach_diff'] = df['r_reach'] - df['b_reach']
    df['weight_diff'] = df['r_weight'] - df['b_weight']

    df['r_win_rate'] = df['r_wins'] / (df['r_wins'] + df['r_losses'] + 1)
    df['b_win_rate'] = df['b_wins'] / (df['b_wins'] + df['b_losses'] + 1)
    df['win_rate_diff'] = df['r_win_rate'] - df['b_win_rate']

    df['str_acc_diff'] = df['r_str_acc'] - df['b_str_acc']
    df['str_def_diff'] = df['r_str_def'] - df['b_str_def']
    df['td_avg_diff'] = df['r_td_avg'] - df['b_td_avg']
    df['td_def_diff'] = df['r_td_def'] - df['b_td_def']
    df['splm_diff'] = df['r_splm'] - df['b_splm']
    df['sapm_diff'] = df['r_sapm'] - df['b_sapm']

    if 'r_streak' not in df.columns:
        df['r_streak'] = 0
    if 'b_streak' not in df.columns:
        df['b_streak'] = 0
    if 'streak_diff' not in df.columns:
        df['streak_diff'] = df['r_streak'] - df['b_streak']

    return df


def create_symmetric_dataset(df_train, feature_cols=FEATURE_COLS):
    """
    Cria versão simétrica do treino invertendo Red e Blue corners
    para eliminar viés de corner (Corner Bias).
    """
    df_swapped = df_train.copy()

    # Inverte colunas r_ e b_
    for c in feature_cols:
        if c.startswith('r_'):
            partner = 'b_' + c[2:]
            df_swapped[c], df_swapped[partner] = df_train[partner], df_train[c]

    # Inverte diferenciais
    for c in [c for c in feature_cols if c.endswith('_diff')]:
        df_swapped[c] = -df_train[c]

    df_swapped['elo_expected_r'] = 1 - df_train['elo_expected_r']
    df_swapped['target'] = 1 - df_train['target']

    symmetric_df = pd.concat([df_train, df_swapped], ignore_index=True)
    return symmetric_df
