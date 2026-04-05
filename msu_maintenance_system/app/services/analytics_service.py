import pandas as pd
import matplotlib.pyplot as plt
import os
from .database import db_service
from config import Config

class AnalyticsService:
    def __init__(self):
        self.static_dir = Config.STATIC_DIR
    
    def get_category_analytics(self):
        query = "SELECT category, COUNT(*) as count FROM job_requests GROUP BY category"
        data = db_service.execute_query(query)
        return data
    
    def generate_category_chart(self):
        data = self.get_category_analytics()
        if data:
            df = pd.DataFrame(data, columns=['category', 'count'])
            df.plot(kind='bar', x='category', y='count', color='skyblue')
            plt.title('Maintenance Categories Distribution')
            plt.xlabel('Category')
            plt.ylabel('Number of Jobs')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.static_dir, 'category_chart.png')
            plt.savefig(chart_path)
            plt.close()
            return chart_path
        return None
    
    def get_hotspot_analytics(self):
        query = """
            SELECT department, COUNT(*) as issue_count
            FROM job_requests
            GROUP BY department
            ORDER BY issue_count DESC
        """
        return db_service.execute_query(query)
    
    def generate_hotspot_chart(self):
        data = self.get_hotspot_analytics()
        if data:
            df = pd.DataFrame(data, columns=['department', 'issue_count'])
            df.plot(kind='bar', x='department', y='issue_count', color='salmon')
            plt.title('Maintenance Hotspots by Department')
            plt.xlabel('Department')
            plt.ylabel('Number of Issues')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.static_dir, 'hotspots.png')
            plt.savefig(chart_path)
            plt.close()
            return chart_path
        return None
    
    def get_performance_analytics(self):
        query = """
            SELECT 
                a.worker_name, 
                COUNT(*) as jobs_done
            FROM Assignments a
            WHERE a.end_time IS NOT NULL
            GROUP BY a.worker_name
            ORDER BY jobs_done DESC
        """
        return db_service.execute_query(query)
    
    def generate_performance_chart(self):
        data = self.get_performance_analytics()
        if data:
            df = pd.DataFrame(data, columns=['worker_name', 'jobs_done'])
            df.plot(kind='bar', x='worker_name', y='jobs_done', color='lightgreen')
            plt.title('Worker Performance')
            plt.xlabel('Worker')
            plt.ylabel('Jobs Completed')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.static_dir, 'performance.png')
            plt.savefig(chart_path)
            plt.close()
            return chart_path
        return None
    
    def get_trend_analytics(self):
        query = """
            SELECT 
                CAST(date_created AS DATE) as date,
                COUNT(*) as jobs_count
            FROM job_requests
            GROUP BY CAST(date_created AS DATE)
            ORDER BY date
        """
        return db_service.execute_query(query)

analytics_service = AnalyticsService()
