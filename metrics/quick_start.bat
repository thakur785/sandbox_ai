@echo off
echo 🚀 GitHub Metrics System - Quick Start
echo =====================================
echo.
echo Choose what to run:
echo.
echo 1. Enhanced Simple Test (with hardcoded repos/users)
echo 2. Enhanced Dashboard (with team configurations)
echo 3. Basic Simple Test (no authentication needed)
echo 4. Fix Rate Limit Issues (setup GitHub token)
echo 5. Debug Import Issues
echo 6. Install Dependencies
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🧪 Running Enhanced Simple Test...
    python simple_test_enhanced.py
) else if "%choice%"=="2" (
    echo.
    echo 📊 Launching Enhanced Dashboard...
    echo 🌐 Opening http://localhost:8501 in your browser...
    streamlit run streamlit_dashboard_enhanced.py
) else if "%choice%"=="3" (
    echo.
    echo 🔧 Running Basic Simple Test...
    python simple_test.py
) else if "%choice%"=="4" (
    echo.
    echo � Fixing Rate Limit Issues...
    python fix_rate_limit.py
) else if "%choice%"=="5" (
    echo.
    echo �🔍 Running Import Debug Test...
    python test_import_debug.py
) else if "%choice%"=="6" (
    echo.
    echo 📦 Installing Dependencies...
    pip install pygithub streamlit plotly pandas python-dotenv
    echo ✅ Installation complete!
) else (
    echo ❌ Invalid choice
)

echo.
pause
