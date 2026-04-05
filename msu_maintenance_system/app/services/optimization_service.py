"""
Prescriptive Optimization Service - MSU Maintenance System
Provides automated assignment recommendations and optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import text
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

class OptimizationService:
    """Prescriptive optimization service"""
    
    def __init__(self):
        self.sla_thresholds = {
            'urgent': 4,    # 4 hours
            'high': 8,      # 8 hours
            'medium': 24,    # 24 hours
            'low': 72        # 72 hours
        }
        self.confidence_threshold = 0.7
    
    def recommend_worker(self, job_id: int) -> Dict:
        """Recommend best worker for job assignment"""
        try:
            # Get job details
            job_query = text("""
                SELECT jr.id, jr.category_id, jr.priority, jr.description,
                       d.name as department_name
                FROM job_requests jr
                JOIN departments d ON jr.department_id = d.id
                WHERE jr.id = :job_id
            """)
            job_result = db.session.execute(job_query, {'job_id': job_id})
            job = job_result.fetchone()
            
            if not job:
                return {'error': 'Job not found'}
            
            # Get available workers
            worker_query = text("""
                SELECT u.id, u.full_name, u.skill_level, u.department_id,
                       COUNT(jr.id) as current_workload,
                       AVG(DATEDIFF(hour, jr.created_at, jr.completed_at)) as avg_resolution_time
                FROM users u
                LEFT JOIN job_requests jr ON u.id = jr.assigned_to AND jr.status IN ('assigned', 'in_progress')
                WHERE u.is_active = 1
                GROUP BY u.id, u.full_name, u.skill_level, u.department_id
            """)
            worker_result = db.session.execute(worker_query)
            workers = pd.DataFrame(worker_result.fetchall(), columns=worker_result.keys())
            
            if workers.empty:
                return {'error': 'No available workers'}
            
            # Calculate recommendation scores
            recommendations = []
            for _, worker in workers.iterrows():
                score = self._calculate_worker_score(job, worker)
                recommendations.append({
                    'worker_id': worker['id'],
                    'worker_name': worker['full_name'],
                    'score': score,
                    'skill_match': self._get_skill_match(job['category_id'], worker['id']),
                    'workload_factor': self._get_workload_factor(worker['current_workload']),
                    'performance_factor': self._get_performance_factor(worker['avg_resolution_time'])
                })
            
            # Sort by score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                'job_id': job_id,
                'recommendations': recommendations[:5],  # Top 5
                'best_match': recommendations[0] if recommendations else None,
                'confidence': self._calculate_confidence(recommendations[0]['score'] if recommendations else 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Worker recommendation error: {e}")
            return {'error': str(e)}
    
    def auto_escalate_priority(self) -> Dict:
        """Auto-escalate jobs exceeding SLA thresholds"""
        try:
            # Get jobs that need escalation
            escalation_query = text("""
                SELECT jr.id, jr.title, jr.priority, jr.created_at,
                       DATEDIFF(hour, jr.created_at, GETUTCDATE()) as hours_since_creation,
                       d.name as department_name
                FROM job_requests jr
                JOIN departments d ON jr.department_id = d.id
                WHERE jr.status IN ('assigned', 'in_progress')
                  AND jr.priority != 'escalated'
            """)
            result = db.session.execute(escalation_query)
            jobs = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            escalated_jobs = []
            for _, job in jobs.iterrows():
                sla_hours = self.sla_thresholds.get(job['priority'], 24)
                if job['hours_since_creation'] > sla_hours:
                    escalated_jobs.append({
                        'job_id': job['id'],
                        'title': job['title'],
                        'current_priority': job['priority'],
                        'hours_overdue': job['hours_since_creation'] - sla_hours,
                        'recommended_priority': self._get_escalated_priority(job['priority']),
                        'department': job['department_name']
                    })
            
            return {
                'escalated_jobs': escalated_jobs,
                'total_escalated': len(escalated_jobs),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Auto-escalation error: {e}")
            return {'error': str(e)}
    
    def optimize_job_queue(self) -> Dict:
        """Optimize job queue by expected completion impact"""
        try:
            # Get pending jobs
            queue_query = text("""
                SELECT jr.id, jr.title, jr.priority, jr.category_id, jr.created_at,
                       d.name as department_name,
                       c.name as category_name
                FROM job_requests jr
                JOIN departments d ON jr.department_id = d.id
                JOIN categories c ON jr.category_id = c.id
                WHERE jr.status = 'pending'
                ORDER BY jr.created_at
            """)
            result = db.session.execute(queue_query)
            jobs = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            if jobs.empty:
                return {'optimized_queue': [], 'message': 'No pending jobs'}
            
            # Calculate impact scores
            jobs['impact_score'] = jobs.apply(self._calculate_impact_score, axis=1)
            jobs['urgency_factor'] = jobs['priority'].map({
                'urgent': 4, 'high': 3, 'medium': 2, 'low': 1
            })
            
            # Sort by impact score and urgency
            optimized_queue = jobs.sort_values(['impact_score', 'urgency_factor'], ascending=[False, False])
            
            return {
                'optimized_queue': optimized_queue.to_dict('records'),
                'total_jobs': len(optimized_queue),
                'optimization_applied': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Queue optimization error: {e}")
            return {'error': str(e)}
    
    def get_department_recommendations(self, department_id: int) -> Dict:
        """Get department-specific recommendations"""
        try:
            # Analyze department patterns
            dept_query = text("""
                SELECT d.name, jr.category_id, c.name as category_name,
                       COUNT(*) as job_count,
                       AVG(DATEDIFF(hour, jr.created_at, jr.completed_at)) as avg_resolution_time
                FROM departments d
                JOIN job_requests jr ON d.id = jr.department_id
                JOIN categories c ON jr.category_id = c.id
                WHERE d.id = :dept_id AND jr.status = 'completed'
                  AND jr.created_at >= DATEADD(month, -3, GETUTCDATE())
                GROUP BY d.name, jr.category_id, c.name
                ORDER BY job_count DESC
            """)
            result = db.session.execute(dept_query, {'dept_id': department_id})
            dept_data = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            if dept_data.empty:
                return {'error': 'No department data found'}
            
            # Generate recommendations
            recommendations = []
            for _, row in dept_data.iterrows():
                if row['job_count'] > 5:  # Recurring issues
                    recommendations.append({
                        'category': row['category_name'],
                        'job_count': row['job_count'],
                        'avg_resolution_time': row['avg_resolution_time'],
                        'recommendation': f"Consider preventive maintenance for {row['category_name']}",
                        'priority': 'high' if row['avg_resolution_time'] > 24 else 'medium'
                    })
            
            return {
                'department_name': dept_data['name'].iloc[0],
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'analysis_period': '3 months',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Department recommendations error: {e}")
            return {'error': str(e)}
    
    def _calculate_worker_score(self, job: Dict, worker: Dict) -> float:
        """Calculate worker recommendation score"""
        skill_match = self._get_skill_match(job['category_id'], worker['id'])
        workload_factor = self._get_workload_factor(worker['current_workload'])
        performance_factor = self._get_performance_factor(worker['avg_resolution_time'])
        
        # Weighted score calculation
        score = (skill_match * 0.4) + (workload_factor * 0.3) + (performance_factor * 0.3)
        return score
    
    def _get_skill_match(self, category_id: int, worker_id: int) -> float:
        """Get skill match score"""
        # Simplified skill matching - in production, this would query actual skills
        return np.random.uniform(0.6, 1.0)  # Placeholder
    
    def _get_workload_factor(self, current_workload: int) -> float:
        """Get workload factor"""
        if current_workload == 0:
            return 1.0
        elif current_workload <= 2:
            return 0.8
        elif current_workload <= 5:
            return 0.6
        else:
            return 0.3
    
    def _get_performance_factor(self, avg_resolution_time: float) -> float:
        """Get performance factor"""
        if avg_resolution_time <= 4:
            return 1.0
        elif avg_resolution_time <= 8:
            return 0.8
        elif avg_resolution_time <= 24:
            return 0.6
        else:
            return 0.4
    
    def _calculate_confidence(self, score: float) -> float:
        """Calculate confidence level"""
        return min(1.0, score / 0.8)  # Normalize to 0-1 range
    
    def _get_escalated_priority(self, current_priority: str) -> str:
        """Get escalated priority"""
        escalation_map = {
            'low': 'medium',
            'medium': 'high',
            'high': 'urgent',
            'urgent': 'critical'
        }
        return escalation_map.get(current_priority, 'urgent')
    
    def _calculate_impact_score(self, row) -> float:
        """Calculate job impact score"""
        priority_weight = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        days_waiting = (datetime.now() - row['created_at']).days
        
        return priority_weight.get(row['priority'], 1) * (1 + days_waiting * 0.1)
