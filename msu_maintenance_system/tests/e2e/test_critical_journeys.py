"""
End-to-End Tests for Critical User Journeys
Tests complete workflows from user perspective.
"""

import pytest
import json
from app.domain import JobStatus, Priority


class TestJobManagementJourney:
    """E2E tests for job management workflow."""
    
    def test_complete_job_lifecycle(self, client, sample_user, sample_worker, jwt_headers):
        """Test complete job lifecycle: create -> assign -> start -> complete."""
        # Step 1: Create a job
        job_data = {
            'department': 'Electrical Services',
            'description': 'Broken emergency light in hallway',
            'category': 'electrical',
            'priority': 'HIGH'
        }
        
        response = client.post('/api/v1/jobs',
                             data=json.dumps(job_data),
                             content_type='application/json',
                             headers=jwt_headers)
        
        assert response.status_code == 201
        job = json.loads(response.data)['data']
        job_id = job['id']
        
        # Step 2: Get available workers
        response = client.get('/api/v1/workers/available',
                            headers=jwt_headers)
        
        assert response.status_code == 200
        workers = json.loads(response.data)['data']
        assert len(workers) > 0
        
        # Step 3: Assign worker to job
        assignment_data = {
            'job_id': job_id,
            'worker_id': workers[0]['id']
        }
        
        response = client.post('/api/v1/assignments',
                             data=json.dumps(assignment_data),
                             content_type='application/json',
                             headers=jwt_headers)
        
        assert response.status_code == 201
        assignment = json.loads(response.data)['data']
        assignment_id = assignment['id']
        
        # Step 4: Start the assignment
        response = client.post(f'/api/v1/assignments/{assignment_id}/start',
                             headers=jwt_headers)
        
        assert response.status_code == 200
        updated_assignment = json.loads(response.data)['data']
        assert updated_assignment['status'] == 'IN_PROGRESS'
        
        # Step 5: Complete the assignment
        response = client.post(f'/api/v1/assignments/{assignment_id}/complete',
                             headers=jwt_headers)
        
        assert response.status_code == 200
        completed_assignment = json.loads(response.data)['data']
        assert completed_assignment['status'] == 'COMPLETED'
        
        # Step 6: Verify job status is updated
        response = client.get(f'/api/v1/jobs/{job_id}',
                            headers=jwt_headers)
        
        assert response.status_code == 200
        updated_job = json.loads(response.data)['data']
        assert updated_job['status'] == 'COMPLETED'
    
    def test_worker_management_journey(self, client, sample_admin_user, admin_jwt_headers):
        """Test complete worker management workflow."""
        # Step 1: Create multiple workers
        workers_data = [
            {
                'full_name': 'John Smith',
                'department': 'Electrical Services',
                'skill_category': 'electrical',
                'is_active': True
            },
            {
                'full_name': 'Jane Doe',
                'department': 'Plumbing Services',
                'skill_category': 'plumbing',
                'is_active': True
            },
            {
                'full_name': 'Bob Johnson',
                'department': 'Mechanical Services',
                'skill_category': 'mechanical',
                'is_active': True
            }
        ]
        
        created_workers = []
        for worker_data in workers_data:
            response = client.post('/api/v1/workers',
                                 data=json.dumps(worker_data),
                                 content_type='application/json',
                                 headers=admin_jwt_headers)
            
            assert response.status_code == 201
            worker = json.loads(response.data)['data']
            created_workers.append(worker)
        
        # Step 2: Get worker statistics
        response = client.get('/api/v1/workers/stats',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        stats = json.loads(response.data)['data']
        assert stats['total_workers'] >= 3
        
        # Step 3: Search for electrical workers
        response = client.get('/api/v1/workers?skill_category=electrical',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        electrical_workers = json.loads(response.data)['data']
        assert len(electrical_workers) >= 1
        
        # Step 4: Get worker performance
        response = client.get(f'/api/v1/workers/{electrical_workers[0]["id"]}/performance',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        performance = json.loads(response.data)['data']
        assert 'completion_rate' in performance
        
        # Step 5: Deactivate a worker
        response = client.put(f'/api/v1/workers/{created_workers[0]["id"]}',
                             data=json.dumps({'is_active': False}),
                             content_type='application/json',
                             headers=admin_jwt_headers)
        
        assert response.status_code == 200
        updated_worker = json.loads(response.data)['data']
        assert updated_worker['is_active'] is False
    
    def test_material_tracking_journey(self, client, sample_user, sample_job, jwt_headers):
        """Test material tracking workflow."""
        # Step 1: Add materials to job
        materials_data = [
            {
                'job_id': sample_job.id,
                'item_name': 'LED Bulb',
                'unit': 'pieces',
                'quantity_required': 5.0
            },
            {
                'job_id': sample_job.id,
                'item_name': 'Electrical Wire',
                'unit': 'meters',
                'quantity_required': 10.0
            }
        ]
        
        created_materials = []
        for material_data in materials_data:
            response = client.post('/api/v1/materials',
                                 data=json.dumps(material_data),
                                 content_type='application/json',
                                 headers=jwt_headers)
            
            assert response.status_code == 201
            material = json.loads(response.data)['data']
            created_materials.append(material)
        
        # Step 2: Get materials for job
        response = client.get(f'/api/v1/materials?job_id={sample_job.id}',
                            headers=jwt_headers)
        
        assert response.status_code == 200
        job_materials = json.loads(response.data)['data']
        assert len(job_materials) == 2
        
        # Step 3: Update material usage
        usage_data = {
            'additional_usage': 3.0
        }
        
        response = client.put(f'/api/v1/materials/{created_materials[0]["id"]}/usage',
                             data=json.dumps(usage_data),
                             content_type='application/json',
                             headers=jwt_headers)
        
        assert response.status_code == 200
        updated_material = json.loads(response.data)['data']
        assert updated_material['quantity_used'] == 3.0
        
        # Step 4: Get material summary
        response = client.get(f'/api/v1/materials/{sample_job.id}/summary',
                            headers=jwt_headers)
        
        assert response.status_code == 200
        summary = json.loads(response.data)['data']
        assert summary['total_materials'] == 2
        assert summary['total_required'] > 0
    
    def test_dashboard_and_analytics_journey(self, client, sample_admin_user, admin_jwt_headers, multiple_jobs):
        """Test dashboard and analytics workflow."""
        # Step 1: Get job statistics
        response = client.get('/api/v1/jobs/stats',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        job_stats = json.loads(response.data)['data']
        assert 'total_jobs' in job_stats
        assert 'pending_jobs' in job_stats
        assert 'department_breakdown' in job_stats
        
        # Step 2: Get assignment statistics
        response = client.get('/api/v1/assignments/stats',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        assignment_stats = json.loads(response.data)['data']
        assert 'total_assignments' in assignment_stats
        assert 'active_assignments' in assignment_stats
        
        # Step 3: Get worker statistics
        response = client.get('/api/v1/workers/stats',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        worker_stats = json.loads(response.data)['data']
        assert 'total_workers' in worker_stats
        assert 'skill_category_breakdown' in worker_stats
        
        # Step 4: Search jobs with filters
        response = client.get('/api/v1/jobs?status=PENDING&priority=HIGH',
                            headers=admin_jwt_headers)
        
        assert response.status_code == 200
        filtered_jobs = json.loads(response.data)['data']
        assert 'items' in filtered_jobs
        assert 'total' in filtered_jobs
    
    def test_user_authentication_journey(self, client):
        """Test complete user authentication workflow."""
        # Step 1: Register a new user
        user_data = {
            'email': 'journey.user@staff.msu.ac.zw',
            'password': 'JourneyPassword123!',
            'confirm_password': 'JourneyPassword123!',
            'role': 'staff'
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        created_user = json.loads(response.data)['data']['user']
        
        # Step 2: Login with the new user
        login_data = {
            'email': 'journey.user@staff.msu.ac.zw',
            'password': 'JourneyPassword123!'
        }
        
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        login_result = json.loads(response.data)['data']
        access_token = login_result['access_token']
        
        # Step 3: Get user profile
        headers = {'Authorization': f'Bearer {access_token}'}
        response = client.get('/api/v1/auth/me',
                            headers=headers)
        
        assert response.status_code == 200
        profile = json.loads(response.data)['data']
        assert profile['email'] == 'journey.user@staff.msu.ac.zw'
        
        # Step 4: Change password
        password_data = {
            'current_password': 'JourneyPassword123!',
            'new_password': 'NewJourneyPassword123!',
            'confirm_password': 'NewJourneyPassword123!'
        }
        
        response = client.post('/api/v1/auth/change-password',
                             data=json.dumps(password_data),
                             content_type='application/json',
                             headers=headers)
        
        assert response.status_code == 200
        
        # Step 5: Login with new password
        new_login_data = {
            'email': 'journey.user@staff.msu.ac.zw',
            'password': 'NewJourneyPassword123!'
        }
        
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(new_login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        new_login_result = json.loads(response.data)['data']
        assert 'access_token' in new_login_result
    
    def test_error_handling_journey(self, client, jwt_headers):
        """Test error handling across various endpoints."""
        # Test non-existent job
        response = client.get('/api/v1/jobs/999',
                            headers=jwt_headers)
        
        assert response.status_code == 404
        error_data = json.loads(response.data)
        assert error_data['success'] is False
        
        # Test invalid data for job creation
        invalid_job_data = {
            'department': '',  # Invalid empty department
            'description': 'Too short',  # Too short description
            'category': 'invalid_category',  # Invalid category
            'priority': 'INVALID_PRIORITY'  # Invalid priority
        }
        
        response = client.post('/api/v1/jobs',
                             data=json.dumps(invalid_job_data),
                             content_type='application/json',
                             headers=jwt_headers)
        
        assert response.status_code == 400
        error_data = json.loads(response.data)
        assert error_data['success'] is False
        
        # Test unauthorized access (no token)
        response = client.get('/api/v1/jobs')
        
        assert response.status_code == 401
        error_data = json.loads(response.data)
        assert error_data['success'] is False
        
        # Test invalid token
        response = client.get('/api/v1/jobs',
                            headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 401
        error_data = json.loads(response.data)
        assert error_data['success'] is False
