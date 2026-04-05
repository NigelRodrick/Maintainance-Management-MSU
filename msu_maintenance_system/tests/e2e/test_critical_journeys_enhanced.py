"""
End-to-End Tests with Playwright
Critical user journeys and mobile viewport testing.
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestCriticalJourneys:
    """Test critical user journeys through the application."""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test."""
        # Navigate to the application
        page.goto("http://localhost:5000")
        
        # Set viewport size for desktop testing
        page.set_viewport_size({"width": 1280, "height": 720})
    
    def test_staff_login_job_submission_flow(self, page: Page):
        """Test staff login → job submission → status tracking flow."""
        
        # Step 1: Staff Login
        page.click("a[href='/login']")
        expect(page).to_have_title("Login - MSU Maintenance System")
        
        # Fill login form
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        
        # Verify successful login
        expect(page).to_have_url("http://localhost:5000/dashboard")
        expect(page.locator("h1")).to_contain_text("Dashboard")
        
        # Step 2: Submit New Job
        page.click("a[href='/jobs/new']")
        expect(page).to_have_title("New Job Request - MSU Maintenance System")
        
        # Fill job form
        page.select_option("select[name='department']", "Electrical Services")
        page.fill("textarea[name='description']", "Broken light fixture in main hallway")
        page.select_option("select[name='category']", "electrical")
        page.select_option("select[name='priority']", "MEDIUM")
        
        # Submit job
        page.click("button[type='submit']")
        
        # Verify job submission
        expect(page).to_have_url("http://localhost:5000/jobs")
        expect(page.locator(".alert-success")).to_contain_text("Job request submitted successfully")
        
        # Step 3: Track Job Status
        # Find the newly submitted job
        job_row = page.locator("table tbody tr").first
        expect(job_row).to_contain_text("Broken light fixture")
        expect(job_row).to_contain_text("PENDING")
        
        # Click on job details
        job_row.click("a[href*='/jobs/']")
        
        # Verify job details page
        expect(page.locator("h1")).to_contain_text("Job Details")
        expect(page.locator(".job-status")).to_contain_text("PENDING")
        
        # Step 4: Check Job History
        page.click("a[href='/jobs']")
        expect(page.locator("table tbody")).to_have_count(1)  # At least one job
    
    def test_supervisor_assignment_workflow(self, page: Page):
        """Test supervisor login → job assignment → worker management flow."""
        
        # Step 1: Supervisor Login
        page.click("a[href='/login']")
        page.fill("input[name='email']", "supervisor.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "SupervisorPassword123!")
        page.click("button[type='submit']")
        
        # Verify supervisor dashboard
        expect(page).to_have_url("http://localhost:5000/dashboard")
        expect(page.locator("h1")).to_contain_text("Dashboard")
        
        # Step 2: View Pending Jobs
        page.click("a[href='/jobs']")
        expect(page.locator("h1")).to_contain_text("Job Requests")
        
        # Filter pending jobs
        page.select_option("select[name='status_filter']", "PENDING")
        page.click("button[type='submit']")
        
        # Verify pending jobs are shown
        pending_jobs = page.locator("table tbody tr")
        expect(pending_jobs).to_have_count_greater_than(0)
        
        # Step 3: Assign Job to Worker
        first_job = pending_jobs.first
        job_description = first_job.locator("td").nth(1).text_content()
        
        first_job.click("a[href*='/assign']")
        
        # Verify assignment page
        expect(page.locator("h1")).to_contain_text("Assign Job")
        expect(page.locator(".job-description")).to_contain_text(job_description)
        
        # Select worker
        page.select_option("select[name='worker_id']", "1")
        page.fill("textarea[name='notes']", "Assign to electrical team")
        
        # Submit assignment
        page.click("button[type='submit']")
        
        # Verify assignment success
        expect(page.locator(".alert-success")).to_contain_text("Job assigned successfully")
        
        # Step 4: Manage Workers
        page.click("a[href='/workers']")
        expect(page.locator("h1")).to_contain_text("Workers")
        
        # Verify worker list
        workers = page.locator("table tbody tr")
        expect(workers).to_have_count_greater_than(0)
        
        # View worker details
        first_worker = workers.first
        worker_name = first_worker.locator("td").nth(0).text_content()
        
        first_worker.click("a[href*='/workers/']")
        
        # Verify worker details
        expect(page.locator("h1")).to_contain_text("Worker Details")
        expect(page.locator(".worker-name")).to_contain_text(worker_name)
    
    def test_admin_user_management(self, page: Page):
        """Test admin login → user management → system configuration flow."""
        
        # Step 1: Admin Login
        page.click("a[href='/login']")
        page.fill("input[name='email']", "admin.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "AdminPassword123!")
        page.click("button[type='submit']")
        
        # Verify admin dashboard
        expect(page).to_have_url("http://localhost:5000/dashboard")
        expect(page.locator("h1")).to_contain_text("Dashboard")
        
        # Step 2: Access User Management
        page.click("a[href='/admin/users']")
        expect(page.locator("h1")).to_contain_text("User Management")
        
        # Verify user list
        users = page.locator("table tbody tr")
        expect(users).to_have_count_greater_than(0)
        
        # Step 3: Create New User
        page.click("a[href='/admin/users/new']")
        expect(page.locator("h1")).to_contain_text("Create User")
        
        # Fill user form
        page.fill("input[name='email']", "new.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "NewUserPassword123!")
        page.fill("input[name='confirm_password']", "NewUserPassword123!")
        page.select_option("select[name='role']", "STAFF")
        page.check("input[name='is_active']")
        
        # Submit user creation
        page.click("button[type='submit']")
        
        # Verify user creation success
        expect(page.locator(".alert-success")).to_contain_text("User created successfully")
        
        # Step 4: View System Configuration
        page.click("a[href='/admin/settings']")
        expect(page.locator("h1")).to_contain_text("System Settings")
        
        # Verify settings sections
        expect(page.locator("h2")).to_contain_text("General Settings")
        expect(page.locator("h2")).to_contain_text("Security Settings")
        expect(page.locator("h2")).to_contain_text("Notification Settings")
    
    def test_job_status_update_workflow(self, page: Page):
        """Test job status update workflow from assignment to completion."""
        
        # Login as supervisor
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "supervisor.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "SupervisorPassword123!")
        page.click("button[type='submit']")
        
        # Navigate to assigned jobs
        page.click("a[href='/jobs']")
        page.select_option("select[name='status_filter']", "IN_PROGRESS")
        page.click("button[type='submit']")
        
        # Select an in-progress job
        in_progress_jobs = page.locator("table tbody tr")
        if in_progress_jobs.count() > 0:
            first_job = in_progress_jobs.first
            first_job.click("a[href*='/jobs/']")
            
            # Update job status
            page.click("button[id='update-status-btn']")
            page.select_option("select[name='status']", "COMPLETED")
            page.fill("textarea[name='completion_notes']", "Job completed successfully")
            page.click("button[type='submit']")
            
            # Verify status update
            expect(page.locator(".alert-success")).to_contain_text("Job status updated successfully")
            expect(page.locator(".job-status")).to_contain_text("COMPLETED")
    
    def test_material_management_workflow(self, page: Page):
        """Test material management workflow for job completion."""
        
        # Login as supervisor
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "supervisor.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "SupervisorPassword123!")
        page.click("button[type='submit']")
        
        # Navigate to a job
        page.click("a[href='/jobs']")
        page.locator("table tbody tr").first.click("a[href*='/jobs/']")
        
        # Add materials
        page.click("button[id='add-material-btn']")
        page.fill("input[name='item_name']", "LED Light Bulb")
        page.select_option("select[name='unit']", "pieces")
        page.fill("input[name='quantity_required']", "5")
        page.fill("input[name='quantity_used']", "3")
        page.click("button[type='submit']")
        
        # Verify material addition
        expect(page.locator(".alert-success")).to_contain_text("Material added successfully")
        expect(page.locator(".materials-list")).to_contain_text("LED Light Bulb")
    
    def test_report_generation_workflow(self, page: Page):
        """Test report generation and download workflow."""
        
        # Login as admin
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "admin.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "AdminPassword123!")
        page.click("button[type='submit']")
        
        # Navigate to reports
        page.click("a[href='/reports']")
        expect(page.locator("h1")).to_contain_text("Reports")
        
        # Generate job summary report
        page.select_option("select[name='report_type']", "job_summary")
        page.fill("input[name='start_date']", "2024-01-01")
        page.fill("input[name='end_date']", "2024-12-31")
        page.click("button[type='submit']")
        
        # Wait for report generation
        page.wait_for_selector(".report-content", timeout=10000)
        
        # Verify report content
        expect(page.locator(".report-content")).to_be_visible()
        expect(page.locator(".report-summary")).to_contain_text("Job Summary Report")
        
        # Download report
        download_promise = page.expect_download()
        page.click("button[id='download-report-btn']")
        download = download_promise.value
        
        # Verify download
        expect(download.suggested_filename).to_match(r".*\.(pdf|xlsx|csv)$")


class TestMobileResponsive:
    """Test mobile responsiveness of the application."""
    
    @pytest.fixture(autouse=True)
    def setup_mobile(self, page: Page):
        """Setup mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:5000")
    
    def test_mobile_login_page(self, page: Page):
        """Test login page on mobile viewport."""
        page.goto("http://localhost:5000/login")
        
        # Verify mobile layout
        expect(page.locator(".login-form")).to_be_visible()
        expect(page.locator("input[name='email']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
        
        # Test mobile keyboard navigation
        page.tap("input[name='email']")
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.press("Tab")  # Move to password field
        expect(page.locator("input[name='password']")).to_be_focused()
    
    def test_mobile_dashboard(self, page: Page):
        """Test dashboard on mobile viewport."""
        # Login first
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        
        # Verify mobile dashboard
        expect(page.locator(".mobile-dashboard")).to_be_visible()
        expect(page.locator(".mobile-nav")).to_be_visible()
        
        # Test mobile navigation
        page.click(".mobile-menu-toggle")
        expect(page.locator(".mobile-menu")).to_be_visible()
        
        # Test touch interactions
        page.tap(".dashboard-card")
        expect(page.locator(".dashboard-card")).to_have_class("active")
    
    def test_mobile_job_submission(self, page: Page):
        """Test job submission on mobile viewport."""
        # Login first
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        
        # Navigate to job submission
        page.click(".mobile-menu-toggle")
        page.click("a[href='/jobs/new']")
        
        # Verify mobile form
        expect(page.locator(".mobile-form")).to_be_visible()
        expect(page.locator("textarea[name='description']")).to_be_visible()
        
        # Test mobile form submission
        page.select_option("select[name='department']", "Electrical Services")
        page.fill("textarea[name='description']", "Mobile test job")
        page.select_option("select[name='category']", "electrical")
        page.select_option("select[name='priority']", "MEDIUM")
        
        # Scroll to submit button (mobile)
        page.scroll_into_view("button[type='submit']")
        page.tap("button[type='submit']")
        
        # Verify submission
        expect(page.locator(".alert-success")).to_contain_text("Job request submitted successfully")
    
    def test_mobile_tables(self, page: Page):
        """Test table responsiveness on mobile."""
        # Login and navigate to jobs
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        page.click(".mobile-menu-toggle")
        page.click("a[href='/jobs']")
        
        # Verify mobile table
        expect(page.locator(".mobile-table")).to_be_visible()
        
        # Test horizontal scrolling
        table = page.locator(".mobile-table")
        table.scroll_into_view_if_needed()
        
        # Test mobile table actions
        first_row = page.locator(".mobile-table .mobile-row").first
        first_row.tap()
        expect(page.locator(".mobile-row-actions")).to_be_visible()


class TestAccessibility:
    """Test accessibility features of the application."""
    
    def test_keyboard_navigation(self, page: Page):
        """Test keyboard navigation throughout the application."""
        page.goto("http://localhost:5000")
        
        # Test keyboard navigation to login
        page.press("Tab")  # Should focus on first interactive element
        expect(page.locator(":focus")).to_be_visible()
        
        # Navigate to login
        page.press("Enter")
        expect(page).to_have_url("http://localhost:5000/login")
        
        # Test form keyboard navigation
        page.press("Tab")  # Email field
        expect(page.locator("input[name='email']")).to_be_focused()
        
        page.press("Tab")  # Password field
        expect(page.locator("input[name='password']")).to_be_focused()
        
        page.press("Tab")  # Submit button
        expect(page.locator("button[type='submit']")).to_be_focused()
        
        # Test form submission with keyboard
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.press("Enter")
        
        # Verify successful login
        expect(page).to_have_url("http://localhost:5000/dashboard")
    
    def test_aria_labels(self, page: Page):
        """Test ARIA labels and landmarks."""
        page.goto("http://localhost:5000")
        
        # Check for main landmarks
        expect(page.locator("main")).to_be_visible()
        expect(page.locator("nav")).to_be_visible()
        expect(page.locator("header")).to_be_visible()
        expect(page.locator("footer")).to_be_visible()
        
        # Check for ARIA labels
        expect(page.locator("[aria-label]")).to_have_count_greater_than(0)
        expect(page.locator("[role='navigation']")).to_be_visible()
        expect(page.locator("[role='main']")).to_be_visible()
    
    def test_focus_management(self, page: Page):
        """Test focus management in dynamic content."""
        page.goto("http://localhost:5000/login")
        
        # Fill and submit login form
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        
        # Check focus after page load
        focused_element = page.locator(":focus")
        if focused_element.count() > 0:
            expect(focused_element).to_be_visible()
    
    def test_color_contrast(self, page: Page):
        """Test color contrast (basic check)."""
        page.goto("http://localhost:5000")
        
        # Check that text is readable (basic check)
        text_elements = page.locator("p, h1, h2, h3, h4, h5, h6, a, button")
        
        for i in range(min(text_elements.count(), 10)):  # Check first 10 elements
            element = text_elements.nth(i)
            styles = element.evaluate("el => getComputedStyle(el)")
            
            # Basic visibility check
            expect(styles["visibility"]).to_equal("visible")
            expect(float(styles["opacity"])).to_be_greater_than(0.5)
    
    def test_screen_reader_compatibility(self, page: Page):
        """Test screen reader compatibility."""
        page.goto("http://localhost:5000")
        
        # Check for semantic HTML
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("nav[aria-label]")).to_be_visible()
        expect(page.locator("main")).to_be_visible()
        
        # Check for form labels
        page.goto("http://localhost:5000/login")
        expect(page.locator("label[for='email']")).to_be_visible()
        expect(page.locator("label[for='password']")).to_be_visible()
        
        # Check for button descriptions
        expect(page.locator("button[aria-label], button[title]")).to_have_count_greater_than(0)


class TestPerformance:
    """Test application performance."""
    
    def test_page_load_performance(self, page: Page):
        """Test page load performance."""
        start_time = time.time()
        
        page.goto("http://localhost:5000")
        page.wait_for_load_state("networkidle")
        
        load_time = time.time() - start_time
        expect(load_time).to_be_less_than(3.0)  # Should load in under 3 seconds
    
    def test_form_submission_performance(self, page: Page):
        """Test form submission performance."""
        page.goto("http://localhost:5000/login")
        
        start_time = time.time()
        
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        
        page.wait_for_url("http://localhost:5000/dashboard")
        
        submission_time = time.time() - start_time
        expect(submission_time).to_be_less_than(2.0)  # Should submit in under 2 seconds
    
    def test_large_table_performance(self, page: Page):
        """Test performance with large data tables."""
        # Login first
        page.goto("http://localhost:5000/login")
        page.fill("input[name='email']", "test.user@staff.msu.ac.zw")
        page.fill("input[name='password']", "TestPassword123!")
        page.click("button[type='submit']")
        
        # Navigate to jobs page
        page.goto("http://localhost:5000/jobs")
        
        start_time = time.time()
        
        # Wait for table to load
        page.wait_for_selector("table tbody tr", timeout=10000)
        
        render_time = time.time() - start_time
        expect(render_time).to_be_less_than(2.0)  # Should render in under 2 seconds
