import os
import shutil
import kagglehub
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
KAGGLE_DIR = os.path.join(ROOT_DIR, 'ufcdataset_kaggle')

REQUIRED_FILES = {
    'ufc': 'UFC.csv',
    'fighter_details': 'fighter_details.csv'
}

def get_data_dir():
    """Retorna o diretório local de dados (./data). Cria se não existir."""
    os.makedirs(DATA_DIR, exist_ok=True)
    return DATA_DIR

def ensure_data():
    """
    Garante que os arquivos CSV necessários estejam presentes em ./data.
    Se a pasta ufcdataset_kaggle/ estiver presente, atualiza para o formato 2026.
    Caso contrário, garante os arquivos de dados padrão.
    """
    data_dir = get_data_dir()
    ufc_csv = os.path.join(data_dir, 'UFC.csv')
    fighter_csv = os.path.join(data_dir, 'fighter_details.csv')
    
    # Se existe o dataset novo 2026 em ufcdataset_kaggle, podemos processar
    if os.path.exists(os.path.join(KAGGLE_DIR, 'master.csv')) and not os.path.exists(ufc_csv):
        print(f"Detectado novo dataset 2026 em '{KAGGLE_DIR}'. Processando via update_dataset_2026...")
        from update_dataset_2026 import process_kaggle_2026
        process_kaggle_2026(kaggle_dir=KAGGLE_DIR, output_dir=DATA_DIR)
    
    missing = [f for f in REQUIRED_FILES.values() if not os.path.exists(os.path.join(data_dir, f))]
    
    if missing:
        print(f"Arquivos ausentes em {data_dir}: {missing}")
        print("Baixando dataset base do Kaggle via kagglehub...")
        download_path = kagglehub.dataset_download("neelagiriaditya/ufc-datasets-1994-2025/versions/3")
        for key, filename in REQUIRED_FILES.items():
            src_file = os.path.join(download_path, filename)
            dest_file = os.path.join(data_dir, filename)
            if os.path.exists(src_file) and not os.path.exists(dest_file):
                shutil.copy2(src_file, dest_file)
                
    file_paths = {key: os.path.join(data_dir, filename) for key, filename in REQUIRED_FILES.items()}
    return file_paths

def load_fights_df():
    """Carrega o DataFrame principal de lutas (UFC.csv)."""
    paths = ensure_data()
    return pd.read_csv(paths['ufc'])

def load_fighters_df():
    """Carrega o DataFrame de detalhes dos lutadores (fighter_details.csv)."""
    paths = ensure_data()
    return pd.read_csv(paths['fighter_details'])

if __name__ == '__main__':
    paths = ensure_data()
    print("Dados verificados com sucesso:")
    for k, p in paths.items():
        print(f"  - {k}: {p} (Existe: {os.path.exists(p)})")
