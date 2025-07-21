<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# GitHub Metrics Collection System

This workspace contains a comprehensive GitHub metrics tracking system that collects DORA metrics, PR cycle times, and developer productivity insights using Apache Airflow and PyGithub.

## Key Components

### Data Collection (`github_metrics/collectors.py`)
- Uses PyGithub library to extract data from GitHub repositories
- Collects pull requests, deployments, issues, and commits
- Handles rate limiting and error recovery
- Supports date range filtering and repository selection

### Metrics Calculation (`github_metrics/metrics.py`)
- **DORAMetrics**: Calculates deployment frequency, lead time, MTTR, and change failure rate
- **PRMetrics**: Analyzes PR cycle times, review patterns, and merge rates  
- **ProductivityMetrics**: Tracks developer activity and collaboration patterns
- Uses pandas for data processing and statistical analysis

### Airflow Integration (`dags/github_metrics_dag.py`)
- Orchestrates daily data collection and metrics calculation
- Implements task dependencies and error handling
- Stores results for historical analysis
- Configurable via Airflow Variables

### Visualization (`github_metrics/dashboard.py`)
- Interactive dashboard using Dash and Plotly
- Real-time metrics display with trend analysis
- Exportable charts for reporting
- Responsive design with Bootstrap components

## Coding Guidelines

### When working with GitHub API:
- Always handle rate limits gracefully
- Use authentication tokens for higher rate limits
- Implement retry logic for transient failures
- Log API usage for monitoring

### When calculating metrics:
- Handle missing or invalid data gracefully
- Use business hours for time calculations when appropriate  
- Provide multiple percentiles for distributions (mean, median, p75, p95)
- Include data quality indicators (sample sizes, outliers)

### When working with Airflow:
- Use XCom for inter-task communication
- Implement proper error handling and logging
- Make tasks idempotent where possible
- Use Airflow Variables for configuration

### When creating visualizations:
- Use consistent color schemes and styling
- Include interactive elements where beneficial
- Provide context and explanations for metrics
- Support multiple time periods and filtering

## Common Patterns

### Data Collection Pattern:
```python
collector = GitHubCollector(token)
data = collector.collect_pull_requests(repo, start_date, end_date)
```

### Metrics Calculation Pattern:
```python
calculator = DORAMetrics(data)
metrics = calculator.get_all_dora_metrics(period_days=30)
```

### Airflow Task Pattern:
```python
def task_function(**context):
    # Get data from previous task
    data = context['task_instance'].xcom_pull(task_ids='previous_task')
    
    # Process data
    result = process_data(data)
    
    # Store result for next task
    context['task_instance'].xcom_push(key='result', value=result)
    return result
```

## Error Handling

- Always wrap GitHub API calls in try-except blocks
- Log meaningful error messages with context
- Continue processing other repositories if one fails
- Provide default values for missing metrics

## Performance Considerations

- Use pagination for large data sets
- Implement caching for frequently accessed data
- Consider using background tasks for long-running operations
- Monitor GitHub API rate limits

## Testing

- Use the `test_metrics.py` script for validation
- Test with different repositories and time periods
- Verify metrics calculations with known data sets
- Test dashboard functionality with sample data
