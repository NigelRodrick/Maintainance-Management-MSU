
from locust import HttpUser, task, between

class MaintenanceSystemUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def login(self):
        self.client.post("/auth/login", json={
            "email": "test@msu.ac.zw",
            "password": "testpassword"
        })
    
    @task
    def view_dashboard(self):
        self.client.get("/dashboard")
    
    @task
    def view_jobs(self):
        self.client.get("/api/v1/jobs")
