# 🥊 Sistema de Predição de Lutas do UFC

<div align="center">

[![English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)
[![Português](https://img.shields.io/badge/Idioma-Portugu%C3%AAs-green.svg)](README.pt-br.md)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Ativo-success.svg)

**Sistema de Inteligência Artificial para Previsão de Lutas do UFC com XGBoost Calibrado e Sistema Elo**

[Funcionalidades](#-funcionalidades) • [Instalação](#-instalação) • [Início Rápido](#-início-rápido) • [Uso](#-uso) • [Performance do Modelo](#-performance-do-modelo) • [Documentação](#-documentação)

</div>

---

## 🎯 Funcionalidades

- 🤖 **Previsões Calibradas com IA** - Modelo XGBoost calibrado via Platt Scaling (~70.2% de acurácia em 2.143 lutas de teste out-of-time)
- 🏆 **Sistema de Rating Elo** - Notas Elo dinâmicas calculadas cronologicamente para 4.581 lutadores ao longo de 11.441 combates
- 🔥 **Momento Competitivo (Streak)** - Considera a sequência ativa de vitórias ou derrotas consecutivas pré-luta
- ⚖️ **Validação de Categorias de Peso** - Impede simulações de lutas irreais entre categorias de peso distantes
- 📊 **Análise Tática do Confronto** - Vantagens físicas, estatísticas de striking (volume/precisão/defesa), grappling (quedas/defesa) e aproveitamento
- 🌐 **CLI Bilíngue** - Suporte completo a Português e Inglês (`python test_predictions.py --pt`)
- 🔍 **Busca de Lutadores** - Pesquisa rápida no banco de dados completo do UFC
- ✅ **Testes Automatizados** - Bateria de testes automatizados (6/6 aprovados) validando arquivos, inferência e simetria de corners

---

## 🚀 Início Rápido

### Pré-requisitos

```bash
Python 3.11+
pip (Gerenciador de pacotes do Python)
```

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/Ninjexxx/ufc_analysisfight.git
cd ufc_analysisfight
```

2. **Crie e ative o ambiente virtual (Opcional, mas recomendado)**
```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\activate.ps1
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Baixe ou atualize o dataset**
```bash
# Download padrão do Kaggle
python download_dataset.py

# Ou se colocou novos dados na pasta ufcdataset_kaggle/:
python update_dataset_2026.py
```

5. **Treine o modelo calibrado**
```bash
python train_xgboost.py
```

6. **Inicie as previsões!**
```bash
# Modo padrão (Inglês)
python test_predictions.py

# Ou com saídas em Português:
python test_predictions.py --pt
```

---

## 💡 Uso da Interface CLI

### Modo Interativo

```bash
python test_predictions.py --pt
```

**Opções do Menu:**
- `1` - Prever luta entre dois atletas
- `2` - Buscar lutadores no banco de dados
- `3` - Alternar idioma (Switch to English)
- `4` - Sair

### Exemplo de Uso em Código Python

```python
from test_predictions import predict_fight, search_fighter

# Buscar lutadores
search_fighter("Jones", lang="pt")

# Fazer a previsão de um combate
predict_fight("Jon Jones", "Stipe Miocic", lang="pt")
```

### Exemplo de Saída no Terminal

```text
============================================================
PREVISÃO DE LUTA - MODELO XGBOOST CALIBRADO + ELO
============================================================

Jon Jones (22-1-0) | Elo: 1796 | +19 vitórias seguidas - Heavyweight
  vs
Stipe Miocic (14-5-0) | Elo: 1666 | 2 derrotas seguidas - Heavyweight

------------------------------------------------------------
VENCEDOR PREVISTO: Jon Jones
CONFIANÇA (Probabilidade Calibrada): 70.2%

Probabilidades:
  Jon Jones: 70.2%
  Stipe Miocic: 29.8%
============================================================

ANÁLISE ESTATÍSTICA DO CONFRONTO:

Momento Competitivo (Sequência):
  Jon Jones: +19 vitórias seguidas
  Stipe Miocic: 2 derrotas seguidas

Rating Elo Histórico:
  Jon Jones: 1796
  Stipe Miocic: 1666
  Diferença de Elo: 131 pontos a favor de Jon Jones

Vantagens Físicas:
  - Jon Jones tem 10.2cm de vantagem de envergadura

Estatísticas de Striking:
  Jon Jones: 4.38 golpes/min | 58% precisão | 64% defesa
  Stipe Miocic: 4.67 golpes/min | 52% precisão | 52% defesa

Estatísticas de Grappling:
  Jon Jones: 1.89 quedas/luta | 45% precisão | 95% defesa
  Stipe Miocic: 1.74 quedas/luta | 34% precisão | 65% defesa
```

---

## ⚖️ Validação de Categorias de Peso

O sistema **impede casamentos de lutas irreais** aplicando as regras oficiais do UFC:

### ✅ Lutas Válidas
- **Mesma categoria de peso**: Peso Leve vs Peso Leve
- **Categorias adjacentes**: Peso Leve vs Peso Meio-Médio (máximo de 1 categoria de diferença)

### ❌ Lutas Inválidas
- Peso Pena vs Peso Meio-Pesado (4 categorias de diferença)
- Peso Mosca vs Peso Pesado (6 categorias de diferença)

---

## 📊 Performance do Modelo

### Métricas de Validação Temporal Cega (2023–2026)

| Métrica | Valor |
|--------|-------|
| **Algoritmo** | XGBoost Calibrado (`CalibratedClassifierCV`) |
| **Acurácia Out-of-Time** | ~70.2% (2.143 lutas de teste) |
| **AUC-ROC** | 0.7744 |
| **Brier Score (Erro Quadrático)** | 0.1952 / 0.2066 |
| **Atributos (Features)** | 47 (Elo, físicos, striking, grappling, streaks, diferenciais) |
| **Histórico de Treino** | 11.441 combates (1993–2026) com simetria de corners |
| **Total de Lutadores** | 4.581 atletas |

### Categorias de Atributos

1. **Rating Elo Histórico**: Habilidade e momento dinâmico pré-luta
2. **Medidas Físicas**: Altura, peso e envergadura (em cm/kg)
3. **Métricas de Striking**: Golpes significativos/min, precisão de acerto, dano absorvido e taxa de defesa
4. **Métricas de Grappling**: Quedas a cada 15 min, precisão de quedas, defesa de quedas (TDD) e finalizações
5. **Momento Competitivo**: Sequência ativa de vitórias/derrotas consecutivas ao entrar no octógono
6. **Diferenciais Relativos**: Subtrações simétricas eliminando o viés do Red Corner

---

## 🧪 Testes Automatizados

### Executar a Suíte Completa de Testes

```bash
python run_tests.py
```

### Script Rápido para Windows

```bash
test_quick.bat
```

### Cobertura dos Testes (6/6 Passando)
- ✅ Validação de existência de arquivos
- ✅ Carregamento dos modelos serializados
- ✅ Carregamento das bases de dados
- ✅ Predições de confrontos conhecidos
- ✅ Validação de categorias de peso oficiais
- ✅ Teste de simetria de predições ($P(A>B) + P(B>A) \approx 1.0$)

---

## 📁 Estrutura do Projeto

```
ufc_analysisfight/
├── 📄 test_predictions.py                  # CLI interativa bilíngue de predições
├── 📄 train_xgboost.py                     # Treinamento e calibração do XGBoost
├── 📄 train_model.py                       # Treinamento do Random Forest baseline
├── 📄 calculate_elo.py                     # Motor de rating Elo histórico
├── 📄 feature_engineering.py               # Extrator padronizado de 47 atributos e simetria
├── 📄 data_loader.py                       # Gerenciador de download dinâmico e caminhos relativos
├── 📄 update_dataset_2026.py               # Pipeline ETL para os dados atualizados de 2026
├── 📄 run_tests.py                         # Suíte completa de testes automatizados
├── 📄 build_pdf_report.py                  # Gerador do Relatório Técnico oficial em PDF
├── 📄 build_banking_comparison_pdf.py      # Gerador do Estudo Comparativo UFC vs Banco em PDF
├── 📄 requirements.txt                     # Dependências fixadas do projeto
├── 🤖 ufc_xgboost_model.pkl               # Modelo XGBoost calibrado treinado
├── 🤖 ufc_model.pkl                        # Modelo Random Forest treinado
├── 📊 data/                                # Diretório de dados processados
│   ├── UFC.csv                             # 11.441 lutas processadas (1993–2026)
│   ├── fighter_details.csv                 # 4.581 atletas com registros e medidas
│   ├── fighter_elo_ratings.csv             # Ranking Elo atualizado
│   └── elo_history.csv                     # Histórico completo de evolução do Elo
├── 📑 DOCUMENTACAO_TECNICA_UFC_PREDICTION.pdf # Whitepaper técnico de engenharia (PDF)
├── 📑 UFC X BANCO.pdf                      # Estudo comparativo de Machine Learning (PDF)
├── 📖 README.md                            # Documentação principal em Inglês
└── 📖 README.pt-br.md                      # Esta documentação em Português
```

---

## 📚 Documentação Técnica Adicional

- [Relatório Técnico de Engenharia (PDF)](DOCUMENTACAO_TECNICA_UFC_PREDICTION.pdf)
- [Estudo Comparativo: UFC vs Machine Learning Bancário (PDF)](UFC%20X%20BANCO.pdf)
- [Análise de Calibração de Probabilidades](MODEL_OVERCONFIDENCE.md)
- [Guia de Validação de Categorias de Peso](WEIGHT_CLASS_VALIDATION.md)

---

## 👤 Autor

**Arthur Santos**

- GitHub: [@Ninjexxx](https://github.com/Ninjexxx)
- LinkedIn: [Arthur Santos](https://linkedin.com/in/arthursantos0202)

---

## 📝 Licença

Este projeto é distribuído sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
