# 🥊 UFC Fight Prediction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Machine Learning system to predict UFC fight outcomes using XGBoost**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Model Performance](#-model-performance) • [Documentation](#-documentation)

</div>

---

## 🎯 Features

- 🤖 **AI-Powered Predictions** - XGBoost machine learning model with 60-65% accuracy
- ⚖️ **Weight Class Validation** - Prevents unrealistic matchups between distant weight classes
- 📊 **Detailed Analysis** - Physical advantages, striking stats, grappling stats, and win rates
- 🔍 **Fighter Search** - Quick search through the entire UFC fighter database
- 💻 **Interactive CLI** - Easy-to-use command-line interface
- ✅ **Automated Testing** - Complete test suite for reliability

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
pip (Python package manager)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ufc-fight-prediction.git
cd ufc-fight-prediction
```

2. **Install dependencies**
```bash
pip install pandas numpy scikit-learn xgboost kagglehub
```

3. **Download dataset**
```bash
python download_dataset.py
```

4. **Train the model**
```bash
python train_xgboost.py
```

5. **Start predicting!**
```bash
python test_predictions.py
```

---

## 💡 Usage

### Interactive Mode

```bash
python test_predictions.py
```

**Menu Options:**
- `1` - Predict fight between two fighters
- `2` - Search for fighters in database
- `3` - Exit

### Example Predictions

```python
from test_predictions import predict_fight, search_fighter

# Search for a fighter
search_fighter("Jones")

# Predict a fight
predict_fight("Jon Jones", "Stipe Miocic")
```

### Output Example

```
============================================================
FIGHT PREDICTION - XGBOOST MODEL
============================================================

Jon Jones (28-1-0) - Light Heavyweight
  vs
Stipe Miocic (20-5-0) - Heavyweight

------------------------------------------------------------
PREDICTED WINNER: Jon Jones
CONFIDENCE: 67.3%

Probabilities:
  Jon Jones: 67.3%
  Stipe Miocic: 32.7%
============================================================

MATCHUP ANALYSIS:

Physical advantages:
  - Jon Jones has 8.0cm more reach

Win rate:
  Jon Jones: 96.6%
  Stipe Miocic: 80.0%

Striking statistics:
  Jon Jones: 4.38 strikes/min | 58% accuracy | 64% defense
  Stipe Miocic: 4.67 strikes/min | 52% accuracy | 52% defense

Grappling statistics:
  Jon Jones: 1.89 TD/fight | 45% accuracy | 95% defense
  Stipe Miocic: 1.74 TD/fight | 34% accuracy | 65% defense
```

---

## ⚖️ Weight Class Validation

The system **prevents unrealistic matchups** by enforcing UFC rules:

### ✅ Valid Fights
- **Same weight class**: Lightweight vs Lightweight
- **Adjacent classes**: Lightweight vs Welterweight (max 1 class difference)

### ❌ Invalid Fights
- Featherweight vs Light Heavyweight (4 classes apart)
- Flyweight vs Heavyweight (6 classes apart)

### UFC Weight Classes

| Class | Weight Range (kg) | Weight Range (lbs) |
|-------|------------------|--------------------|
| Strawweight | 0 - 52.16 | 0 - 115 |
| Flyweight | 52.17 - 56.70 | 115 - 125 |
| Bantamweight | 56.71 - 61.23 | 125 - 135 |
| Featherweight | 61.24 - 65.77 | 135 - 145 |
| Lightweight | 65.78 - 70.31 | 145 - 155 |
| Welterweight | 70.32 - 77.11 | 155 - 170 |
| Middleweight | 77.12 - 83.91 | 170 - 185 |
| Light Heavyweight | 83.92 - 92.99 | 185 - 205 |
| Heavyweight | 93.00 - 120.20 | 205 - 265 |

---

## 📊 Model Performance

### Metrics

| Metric | Value |
|--------|-------|
| **Algorithm** | XGBoost Classifier |
| **Accuracy** | 60-65% |
| **AUC-ROC** | 0.60-0.65 |
| **Features** | 39 (physical, striking, grappling, engineered) |
| **Training Data** | UFC fights (1994-2025) |

### Feature Categories

1. **Physical Stats**: Height, weight, reach
2. **Striking Stats**: Strikes per minute, accuracy, defense
3. **Grappling Stats**: Takedowns, accuracy, defense
4. **Engineered Features**: Win rate, stat differences, advantages

### Top Important Features

- Win rate difference
- Total wins difference
- Striking accuracy difference
- Takedown defense difference
- Reach advantage

---

## 🧪 Testing

### Run Complete Test Suite

```bash
python run_tests.py
```

### Quick Test (Windows)

```bash
test_quick.bat
```

### Test Coverage

- ✅ File existence validation
- ✅ Model loading
- ✅ Data loading
- ✅ Fight predictions
- ✅ Fighter search
- ✅ Weight class validation

---

## 📁 Project Structure

```
ufc_analysis/
├── 📄 test_predictions.py       # Interactive prediction system
├── 📄 train_xgboost.py          # XGBoost model training
├── 📄 train_model.py            # Random Forest training (alternative)
├── 📄 predict_matchup.py        # Example predictions
├── 📄 run_tests.py              # Automated test suite
├── 📄 download_dataset.py       # Dataset downloader
├── 📄 explore_data.py           # Data exploration
├── 📄 test_quick.bat            # Quick test script (Windows)
├── 🤖 ufc_xgboost_model.pkl    # Trained XGBoost model
├── 🤖 ufc_model.pkl             # Trained Random Forest model
├── 📖 README.md                 # This file
├── 📖 WEIGHT_CLASS_VALIDATION.md # Weight class documentation
├── 📖 MODEL_OVERCONFIDENCE.md   # Model calibration guide
└── 📖 TRANSLATION_SUMMARY.md    # Translation documentation
```

---

## 🔧 Technologies Used

### Core Technologies

- **Python 3.8+** - Programming language
- **XGBoost** - Gradient boosting ML algorithm
- **scikit-learn** - ML framework and utilities
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### Machine Learning

- **Supervised Learning** - Classification task
- **Ensemble Learning** - XGBoost (200 trees)
- **Feature Engineering** - 39 engineered features
- **Cross-validation** - Model evaluation

---

## 📚 Documentation

- [Weight Class Validation Guide](WEIGHT_CLASS_VALIDATION.md)
- [Model Overconfidence Analysis](MODEL_OVERCONFIDENCE.md)
- [Translation Summary](TRANSLATION_SUMMARY.md)

---

## 🐛 Known Issues

### Model Overconfidence

The model tends to be overconfident in predictions:
- 37% of predictions have >90% confidence
- Real UFC fights are more unpredictable

**Solution**: See [MODEL_OVERCONFIDENCE.md](MODEL_OVERCONFIDENCE.md) for calibration techniques.

---

## 🚧 Future Improvements

- [ ] Probability calibration for realistic confidence levels
- [ ] Add fighter age and experience features
- [ ] Implement neural network models
- [ ] Fight style matchup analysis
- [ ] Web interface (Flask/Streamlit)
- [ ] Real-time odds comparison
- [ ] Historical fight timeline analysis
- [ ] Injury and layoff tracking

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Arthur Santos**

- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- **Dataset**: [UFC Datasets 1994-2025](https://www.kaggle.com/datasets/neelagiriaditya/ufc-datasets-1994-2025) by Neelagiri Aditya
- **XGBoost**: Tianqi Chen and Carlos Guestrin
- **UFC**: Ultimate Fighting Championship for the amazing sport

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

<div align="center">

**Made with ❤️ and 🥊 by Arthur Santos**

[⬆ Back to Top](#-ufc-fight-prediction-system)

</div>
