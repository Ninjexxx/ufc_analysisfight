@echo off
echo ========================================
echo QUICK TEST - UFC ANALYSIS
echo ========================================
echo.

echo [1/3] Checking installation...
python -c "import pandas, numpy, xgboost, sklearn; print('OK - Libraries installed')" 2>nul
if errorlevel 1 (
    echo ERROR: Install dependencies with: pip install pandas numpy scikit-learn xgboost kagglehub
    pause
    exit /b 1
)

echo [2/3] Checking model...
if not exist "ufc_xgboost_model.pkl" (
    echo WARNING: Model not found. Run: python train_xgboost.py
    pause
    exit /b 1
)
echo OK - Model found

echo [3/3] Running tests...
python run_tests.py

echo.
pause
