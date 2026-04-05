"""
Plotly Dash Application - MSU Maintenance System
Interactive analytics dashboards
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.analytics import AnalyticsModule
import redis
import json

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Initialize services
analytics = AnalyticsModule()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

app.layout = html.Div([
    html.H1("MSU Maintenance Analytics Dashboard", 
              style={'textAlign': 'center', 'marginBottom': 30}),
    
    # Date range selector
    html.Div([
        html.Label("Select Date Range:"),
        dcc.DatePickerRange(
            id='date-range-picker',
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            display_format='YYYY-MM-DD'
        )
    ], style={'marginBottom': 20}),
    
    # Tabs for different views
    dcc.Tabs(id='tabs', value='overview', children=[
        dcc.Tab(label='Overview', value='overview'),
        dcc.Tab(label='Department Performance', value='departments'),
        dcc.Tab(label='Worker Analytics', value='workers'),
        dcc.Tab(label='Job Trends', value='trends'),
        dcc.Tab(label='Material Analysis', value='materials'),
    ]),
    
    # Content area
    html.Div(id='tab-content', style={'marginTop': 20}),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 seconds
        n_intervals=0
    )
])

@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('interval-component', 'n_intervals')]
)
def update_tab_content(active_tab, start_date, end_date, n_intervals):
    """Update tab content based on active tab"""
    
    # Get cached data or fetch new data
    cache_key = f"dashboard_{active_tab}_{start_date}_{end_date}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        data = json.loads(cached_data)
    else:
        # Fetch fresh data
        if active_tab == 'overview':
            data = get_overview_data(start_date, end_date)
        elif active_tab == 'departments':
            data = get_department_data(start_date, end_date)
        elif active_tab == 'workers':
            data = get_worker_data(start_date, end_date)
        elif active_tab == 'trends':
            data = get_trends_data(start_date, end_date)
        elif active_tab == 'materials':
            data = get_material_data(start_date, end_date)
        else:
            data = {}
        
        # Cache for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(data))
    
    # Return appropriate content
    if active_tab == 'overview':
        return create_overview_layout(data)
    elif active_tab == 'departments':
        return create_department_layout(data)
    elif active_tab == 'workers':
        return create_worker_layout(data)
    elif active_tab == 'trends':
        return create_trends_layout(data)
    elif active_tab == 'materials':
        return create_material_layout(data)
    else:
        return html.Div("Select a tab to view analytics")

def get_overview_data(start_date, end_date):
    """Get overview dashboard data"""
    dashboard_data = analytics.get_dashboard_data()
    return dashboard_data

def create_overview_layout(data):
    """Create overview dashboard layout"""
    return html.Div([
        html.H2("System Overview"),
        
        # Key metrics cards
        html.Div([
            html.Div([
                html.H3(f"{data.get('department_summary', {}).get('total_jobs', 0)}"),
                html.P("Total Jobs")
            ], className='metric-card', style={'backgroundColor': '#007bff'}),
            
            html.Div([
                html.H3(f"{data.get('department_summary', {}).get('departments', 0)}"),
                html.P("Departments")
            ], className='metric-card', style={'backgroundColor': '#28a745'}),
            
            html.Div([
                html.H3(f"{data.get('worker_performance', {}).get('total_workers', 0)}"),
                html.P("Workers")
            ], className='metric-card', style={'backgroundColor': '#ffc107'}),
            
            html.Div([
                html.H3(f"{data.get('sla_compliance', {}).get('overall_compliance_rate', 0):.1f}%"),
                html.P("SLA Compliance")
            ], className='metric-card', style={'backgroundColor': '#dc3545'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 30}),
        
        # Quick charts
        html.Div([
            dcc.Graph(
                id='priority-distribution',
                figure=px.pie(
                    values=list(data.get('job_trends', {}).get('priority_breakdown', {}).values()),
                    names=list(data.get('job_trends', {}).get('priority_breakdown', {}).keys()),
                    title="Job Priority Distribution"
                )
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(
                id='completion-trend',
                figure=px.line(
                    title="Job Completion Trend",
                    x=['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    y=[45, 52, 48, 58],
                    labels={'x': 'Week', 'y': 'Jobs Completed'}
                )
            )
        ], style={'width': '48%', 'float': 'right'})
    ])

def get_department_data(start_date, end_date):
    """Get department performance data"""
    dept_data = analytics.get_department_summary()
    return dept_data

def create_department_layout(data):
    """Create department performance layout"""
    return html.Div([
        html.H2("Department Performance"),
        
        dcc.Graph(
            figure=px.bar(
                x=data.get('departments', []),
                y=data.get('job_counts', []),
                title="Jobs by Department",
                labels={'x': 'Department', 'y': 'Job Count'}
            )
        ),
        
        dcc.Graph(
            figure=px.scatter(
                x=data.get('avg_resolution_times', []),
                y=data.get('completion_rates', []),
                text=data.get('departments', []),
                title="Resolution Time vs Completion Rate",
                labels={'x': 'Avg Resolution Time (hours)', 'y': 'Completion Rate (%)'}
            )
        )
    ])

def get_worker_data(start_date, end_date):
    """Get worker performance data"""
    worker_data = analytics.get_worker_performance()
    return worker_data

def create_worker_layout(data):
    """Create worker analytics layout"""
    return html.Div([
        html.H2("Worker Performance"),
        
        dcc.Graph(
            figure=px.bar(
                x=data.get('worker_names', []),
                y=data.get('jobs_completed', []),
                title="Jobs Completed by Worker",
                labels={'x': 'Worker', 'y': 'Jobs Completed'}
            )
        ),
        
        dcc.Graph(
            figure=px.box(
                x=data.get('worker_names', []),
                y=data.get('efficiency_scores', []),
                title="Worker Efficiency Distribution",
                labels={'x': 'Worker', 'y': 'Efficiency Score'}
            )
        )
    ])

def get_trends_data(start_date, end_date):
    """Get job trends data"""
    trends_data = analytics.get_job_trends()
    return trends_data

def create_trends_layout(data):
    """Create trends layout"""
    return html.Div([
        html.H2("Job Trends"),
        
        dcc.Graph(
            figure=px.line(
                x=data.get('dates', []),
                y=data.get('job_counts', []),
                title="Job Trends Over Time",
                labels={'x': 'Date', 'y': 'Job Count'}
            )
        ),
        
        dcc.Graph(
            figure=px.area(
                x=data.get('categories', []),
                y=data.get('category_counts', []),
                title="Job Categories",
                labels={'x': 'Category', 'y': 'Job Count'}
            )
        )
    ])

def get_material_data(start_date, end_date):
    """Get material usage data"""
    material_data = analytics.get_material_analytics()
    return material_data

def create_material_layout(data):
    """Create material analysis layout"""
    return html.Div([
        html.H2("Material Usage Analysis"),
        
        dcc.Graph(
            figure=px.pie(
                values=data.get('cost_by_category', {}).values(),
                names=list(data.get('cost_by_category', {}).keys()),
                title="Material Cost by Category"
            )
        ),
        
        dcc.Graph(
            figure=px.bar(
                x=data.get('material_names', []),
                y=data.get('usage_counts', []),
                title="Most Used Materials",
                labels={'x': 'Material', 'y': 'Usage Count'}
            )
        )
    ])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
