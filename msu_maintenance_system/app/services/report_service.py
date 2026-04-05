import pandas as pd
from datetime import datetime
import os
from .database import db_service
from .job_service import job_service
from .assignment_service import assignment_service
from .material_service import material_service
from config import Config

class ReportService:
    def __init__(self):
        self.reports_dir = Config.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_comprehensive_report(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"maintenance_report_{timestamp}.xlsx"
        filepath = os.path.join(self.reports_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Jobs sheet
            jobs_data = job_service.get_all_jobs()
            if jobs_data:
                jobs_df = pd.DataFrame(jobs_data, columns=[
                    'id', 'department', 'description', 'category', 
                    'priority', 'status', 'date_created'
                ])
                jobs_df.to_excel(writer, sheet_name='Jobs', index=False)
            
            # Assignments sheet
            assignments_query = """
                SELECT a.id, a.job_id, a.worker_name, a.start_time, a.end_time,
                       j.department, j.category
                FROM Assignments a
                JOIN JobRequests j ON a.job_id = j.id
            """
            assignments_data = db_service.execute_query(assignments_query)
            if assignments_data:
                assignments_df = pd.DataFrame(assignments_data, columns=[
                    'assignment_id', 'job_id', 'worker_name', 'start_time', 
                    'end_time', 'department', 'category'
                ])
                assignments_df.to_excel(writer, sheet_name='Assignments', index=False)
            
            # Materials sheet
            materials_query = """
                SELECT m.id, m.job_id, m.item, m.quantity_required, m.quantity_used,
                       j.department, j.category
                FROM Materials m
                JOIN JobRequests j ON m.job_id = j.id
            """
            materials_data = db_service.execute_query(materials_query)
            if materials_data:
                materials_df = pd.DataFrame(materials_data, columns=[
                    'material_id', 'job_id', 'item', 'quantity_required', 
                    'quantity_used', 'department', 'category'
                ])
                materials_df.to_excel(writer, sheet_name='Materials', index=False)
            
            # Summary sheet
            self._create_summary_sheet(writer)
        
        return filename
    
    def _create_summary_sheet(self, writer):
        stats = job_service.get_job_statistics()
        performance_data = assignment_service.get_worker_performance()
        material_summary = material_service.get_material_summary()
        
        summary_data = []
        
        if stats:
            summary_data.extend([
                ['Total Jobs', stats.total_jobs],
                ['Completed Jobs', stats.completed_jobs],
                ['Pending Jobs', stats.pending_jobs],
                ['In Progress Jobs', stats.in_progress_jobs],
                ['Completion Rate', f"{(stats.completed_jobs / stats.total_jobs * 100):.1f}%" if stats.total_jobs > 0 else "0%"],
                ['', '']
            ])
        
        summary_data.append(['Worker Performance', ''])
        if performance_data:
            for worker in performance_data:
                summary_data.append([f"  {worker.worker_name}", f"{worker.jobs_completed} jobs"])
        
        summary_data.append(['', ''])
        summary_data.append(['Material Usage', ''])
        if material_summary:
            for material in material_summary[:5]:  # Top 5 materials
                summary_data.append([f"  {material.item}", f"{material.total_used} units"])
        
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    def generate_job_report(self, start_date=None, end_date=None):
        query = """
            SELECT department, category, priority, status, COUNT(*) as count
            FROM JobRequests
        """
        params = []
        
        if start_date and end_date:
            query += " WHERE date_created BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += " GROUP BY department, category, priority, status"
        
        if params:
            data = db_service.execute_query(query, params)
        else:
            data = db_service.execute_query(query)
        
        if data:
            df = pd.DataFrame(data, columns=[
                'department', 'category', 'priority', 'status', 'count'
            ])
            return df
        return pd.DataFrame()
    
    def get_report_list(self):
        if os.path.exists(self.reports_dir):
            files = [f for f in os.listdir(self.reports_dir) if f.endswith('.xlsx')]
            files.sort(reverse=True)  # Most recent first
            return files
        return []

report_service = ReportService()
