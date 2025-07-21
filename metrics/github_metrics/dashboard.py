"""
Dashboard module for visualizing GitHub metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)


class MetricsDashboard:
    """Create interactive dashboard for GitHub metrics visualization."""
    
    def __init__(self, metrics_data: Dict[str, Any]):
        """
        Initialize dashboard with metrics data.
        
        Args:
            metrics_data: Dictionary containing all calculated metrics
        """
        self.metrics_data = metrics_data
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup the dashboard layout."""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("GitHub Metrics Dashboard", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            # DORA Metrics Section
            dbc.Row([
                dbc.Col([
                    html.H2("DORA Metrics", className="mb-3"),
                    self._create_dora_cards()
                ])
            ], className="mb-4"),
            
            # Charts Section
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="deployment-frequency-chart")
                ], width=6),
                dbc.Col([
                    dcc.Graph(id="lead-time-chart")
                ], width=6)
            ], className="mb-4"),
            
            # PR Metrics Section
            dbc.Row([
                dbc.Col([
                    html.H2("Pull Request Metrics", className="mb-3"),
                    dcc.Graph(id="pr-cycle-time-chart")
                ])
            ], className="mb-4"),
            
            # Productivity Metrics Section
            dbc.Row([
                dbc.Col([
                    html.H2("Productivity Metrics", className="mb-3"),
                    dcc.Graph(id="productivity-chart")
                ])
            ], className="mb-4"),
            
            # Controls
            dbc.Row([
                dbc.Col([
                    html.H3("Controls", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Period (days):"),
                            dcc.Slider(
                                id="period-slider",
                                min=7,
                                max=90,
                                step=7,
                                value=30,
                                marks={i: f"{i}d" for i in range(7, 91, 14)}
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Repository:"),
                            dcc.Dropdown(
                                id="repo-dropdown",
                                options=[
                                    {"label": "All Repositories", "value": "all"}
                                ],
                                value="all"
                            )
                        ], width=6)
                    ])
                ])
            ])
        ], fluid=True)
    
    def _create_dora_cards(self) -> html.Div:
        """Create DORA metrics cards."""
        dora_metrics = self.metrics_data.get('dora_metrics', {})
        
        cards = []
        
        # Deployment Frequency
        deploy_freq = dora_metrics.get('deployment_frequency', {})
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Deployment Frequency", className="card-title"),
                    html.H2(f"{deploy_freq.get('deployments_per_week', 0):.1f}", 
                           className="text-primary"),
                    html.P("per week", className="card-text")
                ])
            ], className="mb-3")
        )
        
        # Lead Time
        lead_time = dora_metrics.get('lead_time_for_changes', {})
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Lead Time", className="card-title"),
                    html.H2(f"{lead_time.get('median_lead_time_hours', 0):.1f}h", 
                           className="text-info"),
                    html.P("median", className="card-text")
                ])
            ], className="mb-3")
        )
        
        # Mean Time to Recovery
        mttr = dora_metrics.get('mean_time_to_recovery', {})
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H4("MTTR", className="card-title"),
                    html.H2(f"{mttr.get('mean_recovery_time_hours', 0):.1f}h", 
                           className="text-warning"),
                    html.P("mean recovery", className="card-text")
                ])
            ], className="mb-3")
        )
        
        # Change Failure Rate
        cfr = dora_metrics.get('change_failure_rate', {})
        cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Change Failure Rate", className="card-title"),
                    html.H2(f"{cfr.get('change_failure_rate', 0):.1%}", 
                           className="text-danger"),
                    html.P("failure rate", className="card-text")
                ])
            ], className="mb-3")
        )
        
        return dbc.Row([
            dbc.Col(card, width=3) for card in cards
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks."""
        
        @self.app.callback(
            Output('deployment-frequency-chart', 'figure'),
            Input('period-slider', 'value')
        )
        def update_deployment_chart(period_days):
            return self._create_deployment_frequency_chart(period_days)
        
        @self.app.callback(
            Output('lead-time-chart', 'figure'),
            Input('period-slider', 'value')
        )
        def update_lead_time_chart(period_days):
            return self._create_lead_time_chart()
        
        @self.app.callback(
            Output('pr-cycle-time-chart', 'figure'),
            Input('period-slider', 'value')
        )
        def update_pr_chart(period_days):
            return self._create_pr_cycle_time_chart()
        
        @self.app.callback(
            Output('productivity-chart', 'figure'),
            Input('period-slider', 'value')
        )
        def update_productivity_chart(period_days):
            return self._create_productivity_chart()
    
    def _create_deployment_frequency_chart(self, period_days: int = 30) -> go.Figure:
        """Create deployment frequency chart."""
        # Sample data - replace with actual deployment data
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=period_days),
            end=datetime.now(),
            freq='D'
        )
        
        # Simulate deployment data
        deployments = [1 if i % 3 == 0 else 0 for i in range(len(dates))]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=deployments,
            mode='markers+lines',
            name='Deployments',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title="Deployment Frequency Over Time",
            xaxis_title="Date",
            yaxis_title="Deployments per Day",
            height=400
        )
        
        return fig
    
    def _create_lead_time_chart(self) -> go.Figure:
        """Create lead time distribution chart."""
        pr_metrics = self.metrics_data.get('pr_metrics', {})
        cycle_analysis = pr_metrics.get('cycle_time_analysis', {})
        
        # Create sample distribution data
        lead_times = [
            cycle_analysis.get('mean_cycle_time_hours', 24),
            cycle_analysis.get('median_cycle_time_hours', 18),
            cycle_analysis.get('p75_cycle_time_hours', 36),
            cycle_analysis.get('p95_cycle_time_hours', 72)
        ]
        
        labels = ['Mean', 'Median', '75th %ile', '95th %ile']
        
        fig = go.Figure(data=[
            go.Bar(x=labels, y=lead_times, marker_color='lightblue')
        ])
        
        fig.update_layout(
            title="Lead Time Distribution",
            xaxis_title="Percentile",
            yaxis_title="Hours",
            height=400
        )
        
        return fig
    
    def _create_pr_cycle_time_chart(self) -> go.Figure:
        """Create PR cycle time trends chart."""
        # Sample data for demonstration
        weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        cycle_times = [20, 18, 22, 16]
        review_comments = [5, 6, 4, 7]
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("PR Cycle Time", "Review Comments"),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=weeks, y=cycle_times, name="Cycle Time (hours)", line=dict(color='green')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=weeks, y=review_comments, name="Avg Review Comments", line=dict(color='orange')),
            row=2, col=1
        )
        
        fig.update_layout(
            title="PR Metrics Trends",
            height=500
        )
        
        return fig
    
    def _create_productivity_chart(self) -> go.Figure:
        """Create productivity metrics chart."""
        productivity = self.metrics_data.get('productivity_metrics', {})
        commit_activity = productivity.get('commit_activity', {})
        
        # Sample data
        metrics = ['Commits', 'PRs', 'Reviews', 'Lines Changed']
        values = [
            commit_activity.get('total_commits', 50),
            productivity.get('pr_activity', {}).get('total_prs', 10),
            25,  # Sample review count
            commit_activity.get('total_authors', 5) * 1000  # Sample lines changed
        ]
        
        fig = go.Figure(data=[
            go.Bar(x=metrics, y=values, marker_color=['lightgreen', 'lightblue', 'lightyellow', 'lightcoral'])
        ])
        
        fig.update_layout(
            title="Team Productivity Metrics",
            xaxis_title="Metric",
            yaxis_title="Count",
            height=400
        )
        
        return fig
    
    def run(self, host: str = '127.0.0.1', port: int = 8050, debug: bool = True):
        """Run the dashboard."""
        logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)
    
    def get_app(self):
        """Get the Dash app instance."""
        return self.app


def create_static_charts(metrics_data: Dict[str, Any]) -> Dict[str, go.Figure]:
    """
    Create static charts for metrics visualization.
    
    Args:
        metrics_data: Dictionary containing all metrics
        
    Returns:
        Dictionary of plotly figures
    """
    charts = {}
    
    # DORA Metrics Summary
    dora = metrics_data.get('dora_metrics', {})
    dora_values = [
        dora.get('deployment_frequency', {}).get('deployments_per_week', 0),
        dora.get('lead_time_for_changes', {}).get('median_lead_time_hours', 0),
        dora.get('mean_time_to_recovery', {}).get('mean_recovery_time_hours', 0),
        dora.get('change_failure_rate', {}).get('change_failure_rate', 0) * 100
    ]
    dora_labels = ['Deployments/Week', 'Lead Time (h)', 'MTTR (h)', 'Failure Rate (%)']
    
    charts['dora_summary'] = go.Figure(data=[
        go.Bar(x=dora_labels, y=dora_values, marker_color='lightblue')
    ])
    charts['dora_summary'].update_layout(title="DORA Metrics Summary")
    
    # PR Cycle Time Distribution
    pr_metrics = metrics_data.get('pr_metrics', {})
    cycle_analysis = pr_metrics.get('cycle_time_analysis', {})
    
    if cycle_analysis:
        cycle_times = [
            cycle_analysis.get('mean_cycle_time_hours', 0),
            cycle_analysis.get('median_cycle_time_hours', 0),
            cycle_analysis.get('p75_cycle_time_hours', 0),
            cycle_analysis.get('p95_cycle_time_hours', 0)
        ]
        cycle_labels = ['Mean', 'Median', '75th %ile', '95th %ile']
        
        charts['cycle_time_distribution'] = go.Figure(data=[
            go.Bar(x=cycle_labels, y=cycle_times, marker_color='lightgreen')
        ])
        charts['cycle_time_distribution'].update_layout(
            title="PR Cycle Time Distribution",
            yaxis_title="Hours"
        )
    
    return charts
