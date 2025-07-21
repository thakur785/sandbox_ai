# GitHub Metrics Quick Start - PowerShell Version
Write-Host "🚀 GitHub Metrics System - Quick Start" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Choose what to run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Enhanced Simple Test (with hardcoded repos/users)"
Write-Host "2. Enhanced Dashboard (with team configurations)"  
Write-Host "3. Basic Simple Test (no authentication needed)"
Write-Host "4. Install Dependencies"
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🧪 Running Enhanced Simple Test..." -ForegroundColor Cyan
        python simple_test_enhanced.py
    }
    "2" {
        Write-Host ""
        Write-Host "📊 Launching Enhanced Dashboard..." -ForegroundColor Cyan
        Write-Host "🌐 Opening http://localhost:8501 in your browser..." -ForegroundColor Yellow
        python -m streamlit run streamlit_dashboard_enhanced.py
    }
    "3" {
        Write-Host ""
        Write-Host "🔧 Running Basic Simple Test..." -ForegroundColor Cyan
        python simple_test.py
    }
    "4" {
        Write-Host ""
        Write-Host "📦 Installing Dependencies..." -ForegroundColor Cyan
        pip install pygithub streamlit plotly pandas python-dotenv
        Write-Host "✅ Installation complete!" -ForegroundColor Green
    }
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Press Enter to continue"
