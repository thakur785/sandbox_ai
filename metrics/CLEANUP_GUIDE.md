# Production Files to Keep

## 🎯 Essential Files for Repository

### Core Application
- ✅ `simple_test.py` - Basic GitHub API test
- ✅ `simple_test_enhanced.py` - Enhanced test with team configurations
- ✅ `streamlit_dashboard_enhanced.py` - Interactive dashboard
- ✅ `fix_rate_limit.py` - GitHub token setup helper

### Launchers
- ✅ `quick_start.bat` - Windows batch launcher
- ✅ `quick_start.ps1` - PowerShell launcher

### Core Modules
- ✅ `github_metrics/` - All files in this directory
  - `collectors.py`
  - `metrics.py`
  - `dashboard.py`
  - `utils.py`
  - `config.py`
  - `__init__.py`

### Enterprise/Airflow (Optional)
- ✅ `dags/github_metrics_dag.py` - Airflow DAG for scheduled collection

### Configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` - Git ignore rules
- ✅ `README.md` - Documentation
- ✅ `.github/copilot-instructions.md` - AI assistant instructions

## 🗑️ Files to Remove

### Development/Testing Files
- ❌ `demo.py`
- ❌ `example.py`
- ❌ `guide.py`
- ❌ `personal.md`
- ❌ `test_import.py`
- ❌ `test_import_debug.py`
- ❌ `test_metrics.py`
- ❌ `cleanup.py`

### Example/Template Files
- ❌ `user_dashboard_example.py`
- ❌ `user_filtering_example.py`
- ❌ `setup_user_filtering.py`

### Alternative Implementations
- ❌ `create_dashboard.py`
- ❌ `dashboard_ui.py`
- ❌ `launch_dashboard.py`
- ❌ `run_dashboard.py`
- ❌ `simple_launcher.py`
- ❌ `streamlit_dashboard.py` (keep only enhanced version)

### Generated/Temporary Files
- ❌ `github_metrics_dashboard.html`
- ❌ `sample_metrics.json`
- ❌ `requirements-core.txt`

### Development Configuration
- ❌ `setup.py`
- ❌ `pyproject.toml`

## 📁 Final Clean Structure

```
github-metrics/
├── github_metrics/           # Core metrics modules
│   ├── __init__.py
│   ├── collectors.py
│   ├── metrics.py
│   ├── dashboard.py
│   ├── utils.py
│   └── config.py
├── dags/                     # Airflow DAGs (optional)
│   └── github_metrics_dag.py
├── .github/                  # GitHub configurations
│   └── copilot-instructions.md
├── simple_test.py            # Basic test
├── simple_test_enhanced.py   # Enhanced test with teams
├── streamlit_dashboard_enhanced.py  # Interactive dashboard
├── fix_rate_limit.py         # Token setup helper
├── quick_start.bat           # Windows launcher
├── quick_start.ps1           # PowerShell launcher
├── requirements.txt          # Dependencies
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # Documentation
```

## 🎯 Manual Cleanup Commands

### Windows PowerShell:
```powershell
Remove-Item demo.py, example.py, guide.py, personal.md, test_*.py, user_*.py, setup_user_filtering.py, create_dashboard.py, dashboard_ui.py, launch_dashboard.py, run_dashboard.py, simple_launcher.py, streamlit_dashboard.py, github_metrics_dashboard.html, sample_metrics.json, requirements-core.txt, cleanup.py, setup.py, pyproject.toml -Force
```

### Linux/Mac:
```bash
rm -f demo.py example.py guide.py personal.md test_*.py user_*.py setup_user_filtering.py create_dashboard.py dashboard_ui.py launch_dashboard.py run_dashboard.py simple_launcher.py streamlit_dashboard.py github_metrics_dashboard.html sample_metrics.json requirements-core.txt cleanup.py setup.py pyproject.toml
```

After cleanup, you'll have a clean, production-ready GitHub metrics system ready for your repository!
