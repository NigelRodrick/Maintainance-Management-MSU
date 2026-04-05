"""
LEGACY UTILITIES - DEPRECATED

This file contains legacy utility functions with raw pyodbc usage.
New code should use the unified database service instead.

Migration Status: DEPRECATED - Use unified_db_service instead
Removal Target: v2.2.0
"""

import pandas as pd
from .services.unified_db_service import unified_db_service
from .utils.migration_tracker import migration_tracker

# Track usage of legacy utilities
migration_tracker.track_usage('raw pyodbc usage', 'File imported')

def generate_report():
    """DEPRECATED: Use unified_db_service instead"""
    migration_tracker.track_usage('raw pyodbc usage', 'generate_report called')
    
    try:
        # Use unified database service
        df = unified_db_service.read_sql("SELECT * FROM JobRequests")
        df.to_excel("reports/maintenance_report.xlsx", index=False)
    except Exception as e:
        print(f"Error generating report: {e}")


def generate_advanced_report():
    """DEPRECATED: Use unified_db_service instead"""
    migration_tracker.track_usage('raw pyodbc usage', 'generate_advanced_report called')
    
    try:
        # Use unified database service
        jobs = unified_db_service.read_sql("SELECT * FROM JobRequests")
        materials = unified_db_service.read_sql("SELECT * FROM Materials")
        assignments = unified_db_service.read_sql("SELECT * FROM Assignments")

        with pd.ExcelWriter("reports/full_report.xlsx") as writer:
            jobs.to_excel(writer, sheet_name="Jobs", index=False)
            materials.to_excel(writer, sheet_name="Materials", index=False)
            assignments.to_excel(writer, sheet_name="Assignments", index=False)

            # Summary sheet
            summary = pd.DataFrame({
                "Total Jobs": [len(jobs)],
                "Completed Jobs": [len(jobs[jobs["status"] == "Completed"])],
                "Pending Jobs": [len(jobs[jobs["status"] == "Pending"])]
            })

            summary.to_excel(writer, sheet_name="Summary", index=False)
    except Exception as e:
        print(f"Error generating advanced report: {e}")
