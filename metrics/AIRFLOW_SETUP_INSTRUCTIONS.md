# GitHub Metrics with Apache Airflow - Setup Instructions

## Prerequisites
- Apache Airflow 3.0.3 (✅ Already installed in WSL)
- GitHub Personal Access Token
- PyGithub library

## Quick Setup

### 1. Deploy to Airflow
```bash
# In WSL, navigate to the airflow_deployment directory
cd /mnt/c/Work/General/Trainings/AI/sandbox_ai/metrics/airflow_deployment

# Run deployment script
bash deploy_to_airflow.sh
```

### 2. Configure GitHub Token
```bash
# Replace with your actual GitHub token
airflow variables set GITHUB_TOKEN "ghp_your_token_here"
```

### 3. Configure Repositories (Optional)
```bash
# Update with your repositories
airflow variables set GITHUB_REPOSITORIES '["your-org/repo1", "your-org/repo2"]'

# Update team members
airflow variables set TEAM_MEMBERS '["user1", "user2", "user3"]'
```

### 4. Start Airflow (if not running)
```bash
# Start webserver
airflow webserver --port 8080 &

# Start scheduler  
airflow scheduler &
```

### 5. Access Airflow UI
- URL: http://localhost:8080
- Find DAG: `github_metrics_collection`
- Click the toggle to enable it
- Click the play button to trigger manually

## DAG Details

### What it collects:
- Pull Requests (with reviews, comments, cycle times)
- Deployments and releases
- Issues and bug reports
- Commits and collaboration data

### Metrics calculated:
- **DORA Metrics**: Deployment frequency, lead time, MTTR, change failure rate
- **PR Metrics**: Cycle time, review patterns, merge rates
- **Productivity**: Developer activity, collaboration patterns

### Schedule:
- Runs daily at midnight
- Collects data for the last 30 days
- Can be triggered manually anytime

## Troubleshooting

### Common Issues:

1. **Import errors**: Make sure PyGithub is installed in Airflow environment
   ```bash
   pip install PyGithub pandas numpy plotly
   ```

2. **Rate limits**: Ensure GitHub token is set and has proper permissions

3. **DAG not appearing**: Check Airflow logs and ensure files are in correct locations

### Useful Commands:
```bash
# Check DAG status
airflow dags list | grep github_metrics

# Test DAG
airflow dags test github_metrics_collection 2024-01-01

# View logs
airflow logs view github_metrics_collection extract_data 2024-01-01
```

## File Structure in Airflow
```
$AIRFLOW_HOME/
├── dags/
│   ├── github_metrics_dag.py          # Main DAG file
│   └── github_metrics/                # Our package
│       ├── __init__.py
│       ├── collectors.py              # GitHub data collection
│       ├── metrics.py                 # DORA and PR metrics
│       └── dashboard.py               # Dashboard generation
└── airflow_variables.json             # Configuration
```
