from data_loader import ensure_data

if __name__ == "__main__":
    print("Baixando e sincronizando dataset para ./data...")
    paths = ensure_data()
    print("Dataset pronto para uso:")
    for key, path in paths.items():
        print(f"  {key}: {path}")
