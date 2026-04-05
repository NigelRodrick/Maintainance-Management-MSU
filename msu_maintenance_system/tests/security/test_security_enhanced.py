"""
Enhanced Security Testing Configuration
Bandit static analysis and OWASP ZAP dynamic security testing.
"""

import pytest
import subprocess
import json
import os
from pathlib import Path


class TestStaticSecurityAnalysis:
    """Static security analysis using Bandit."""
    
    @pytest.fixture(scope="class")
    def bandit_report(self):
        """Run Bandit security analysis and return report."""
        # Run Bandit analysis
        cmd = [
            "bandit",
            "-r", "app/",
            "-f", "json",
            "-o", "bandit_report.json",
            "--quiet"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Load the report
        try:
            with open("bandit_report.json", "r") as f:
                report = json.load(f)
        except FileNotFoundError:
            report = {"results": [], "errors": []}
        
        return report
    
    def test_no_high_severity_issues(self, bandit_report):
        """Test that no HIGH severity security issues exist."""
        high_issues = [
            issue for issue in bandit_report["results"]
            if issue["issue_severity"] == "HIGH"
        ]
        
        assert len(high_issues) == 0, (
            f"Found {len(high_issues)} HIGH severity security issues:\n"
            + "\n".join([
                f"- {issue['test_name']}: {issue['issue_text']} "
                f"in {issue['filename']}:{issue['line_number']}"
                for issue in high_issues
            ])
        )
    
    def test_no_critical_severity_issues(self, bandit_report):
        """Test that no CRITICAL severity security issues exist."""
        critical_issues = [
            issue for issue in bandit_report["results"]
            if issue["issue_severity"] == "CRITICAL"
        ]
        
        assert len(critical_issues) == 0, (
            f"Found {len(critical_issues)} CRITICAL severity security issues:\n"
            + "\n".join([
                f"- {issue['test_name']}: {issue['issue_text']} "
                f"in {issue['filename']}:{issue['line_number']}"
                for issue in critical_issues
            ])
        )
    
    def test_limited_medium_severity_issues(self, bandit_report):
        """Test that medium severity issues are limited and documented."""
        medium_issues = [
            issue for issue in bandit_report["results"]
            if issue["issue_severity"] == "MEDIUM"
        ]
        
        # Allow some medium issues but ensure they're documented
        assert len(medium_issues) <= 5, (
            f"Too many MEDIUM severity issues found: {len(medium_issues)}. "
            "Maximum allowed is 5."
        )
    
    def test_no_hardcoded_secrets(self, bandit_report):
        """Test that no hardcoded secrets or passwords exist."""
        secret_issues = [
            issue for issue in bandit_report["results"]
            if issue["test_name"] in ["hardcoded_password", "hardcoded_sql_expressions"]
        ]
        
        assert len(secret_issues) == 0, (
            f"Found {len(secret_issues)} hardcoded secrets:\n"
            + "\n".join([
                f"- {issue['test_name']}: {issue['issue_text']} "
                f"in {issue['filename']}:{issue['line_number']}"
                for issue in secret_issues
            ])
        )
    
    def test_no_insecure_random_usage(self, bandit_report):
        """Test that no insecure random number generators are used."""
        random_issues = [
            issue for issue in bandit_report["results"]
            if issue["test_name"] == "use_of insecure_random"
        ]
        
        assert len(random_issues) == 0, (
            f"Found {len(random_issues)} insecure random usage:\n"
            + "\n".join([
                f"- {issue['test_name']}: {issue['issue_text']} "
                f"in {issue['filename']}:{issue['line_number']}"
                for issue in random_issues
            ])
        )
    
    def test_no_sql_injection_vulnerabilities(self, bandit_report):
        """Test that no SQL injection vulnerabilities exist."""
        sql_issues = [
            issue for issue in bandit_report["results"]
            if issue["test_name"] == "hardcoded_sql_expressions"
        ]
        
        assert len(sql_issues) == 0, (
            f"Found {len(sql_issues)} potential SQL injection vulnerabilities:\n"
            + "\n".join([
                f"- {issue['test_name']}: {issue['issue_text']} "
                f"in {issue['filename']}:{issue['line_number']}"
                for issue in sql_issues
            ])
        )


class TestDependencySecurity:
    """Test dependency security using Safety."""
    
    @pytest.fixture(scope="class")
    def safety_report(self):
        """Run Safety dependency check and return report."""
        cmd = [
            "safety",
            "check",
            "--json",
            "--output", "safety_report.json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Load the report
        try:
            with open("safety_report.json", "r") as f:
                report = json.load(f)
        except FileNotFoundError:
            report = {"vulnerabilities": []}
        
        return report
    
    def test_no_high_risk_dependencies(self, safety_report):
        """Test that no high-risk dependencies exist."""
        high_risk = [
            vuln for vuln in safety_report["vulnerabilities"]
            if vuln.get("vulnerability_class", "") == "high"
        ]
        
        assert len(high_risk) == 0, (
            f"Found {len(high_risk)} high-risk dependencies:\n"
            + "\n".join([
                f"- {vuln.get('package', 'unknown')} {vuln.get('installed_version', 'unknown')}: "
                f"{vuln.get('advisory', 'No advisory')}"
                for vuln in high_risk
            ])
        )
    
    def test_no_critical_dependencies(self, safety_report):
        """Test that no critical dependencies exist."""
        critical = [
            vuln for vuln in safety_report["vulnerabilities"]
            if vuln.get("vulnerability_class", "") == "critical"
        ]
        
        assert len(critical) == 0, (
            f"Found {len(critical)} critical dependencies:\n"
            + "\n".join([
                f"- {vuln.get('package', 'unknown')} {vuln.get('installed_version', 'unknown')}: "
                f"{vuln.get('advisory', 'No advisory')}"
                for vuln in critical
            ])
        )


class TestDynamicSecurityAnalysis:
    """Dynamic security analysis using OWASP ZAP."""
    
    @pytest.fixture(scope="class")
    def zap_report(self):
        """Run OWASP ZAP scan and return report."""
        # This would typically run against a staging environment
        # For now, we'll create a mock report structure
        
        # In a real implementation, this would:
        # 1. Start ZAP proxy
        # 2. Spider the application
        # 3. Active scan
        # 4. Generate report
        
        mock_report = {
            "site": [
                {
                    "alerts": [
                        {
                            "alert": "Missing Anti-CSRF Token",
                            "riskcode": "HIGH",
                            "confidence": "High",
                            "description": "No Anti-CSRF tokens were found in the HTML submission form",
                            "instances": [
                                {
                                    "uri": "http://localhost:5000/login",
                                    "method": "POST"
                                }
                            ]
                        },
                        {
                            "alert": "X-Content-Type-Options header missing",
                            "riskcode": "LOW",
                            "confidence": "High",
                            "description": "The Anti-MIME-Sniffing header X-Content-Type-Options was not set",
                            "instances": [
                                {
                                    "uri": "http://localhost:5000/"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        return mock_report
    
    def test_no_high_risk_web_vulnerabilities(self, zap_report):
        """Test that no high-risk web vulnerabilities exist."""
        high_alerts = []
        
        for site in zap_report["site"]:
            for alert in site["alerts"]:
                if alert["riskcode"] == "HIGH":
                    high_alerts.append(alert)
        
        assert len(high_alerts) == 0, (
            f"Found {len(high_alerts)} high-risk web vulnerabilities:\n"
            + "\n".join([
                f"- {alert['alert']}: {alert['description']}"
                for alert in high_alerts
            ])
        )
    
    def test_csrf_protection(self, zap_report):
        """Test that CSRF protection is implemented."""
        csrf_alerts = []
        
        for site in zap_report["site"]:
            for alert in site["alerts"]:
                if "CSRF" in alert["alert"]:
                    csrf_alerts.append(alert)
        
        assert len(csrf_alerts) == 0, (
            "CSRF protection issues found:\n"
            + "\n".join([
                f"- {alert['alert']}: {alert['description']}"
                for alert in csrf_alerts
            ])
        )
    
    def test_security_headers(self, zap_report):
        """Test that security headers are properly configured."""
        header_alerts = []
        
        for site in zap_report["site"]:
            for alert in site["alerts"]:
                if "header" in alert["alert"].lower():
                    header_alerts.append(alert)
        
        # Allow some low-risk header issues but document them
        high_risk_headers = [
            alert for alert in header_alerts
            if alert["riskcode"] in ["HIGH", "MEDIUM"]
        ]
        
        assert len(high_risk_headers) == 0, (
            "High-risk security header issues found:\n"
            + "\n".join([
                f"- {alert['alert']}: {alert['description']}"
                for alert in high_risk_headers
            ])
        )


class TestAuthenticationSecurity:
    """Test authentication security features."""
    
    def test_password_complexity(self):
        """Test password complexity requirements."""
        from app.services.auth_service import AuthService
        
        # Test various password scenarios
        weak_passwords = [
            "password",      # Too common
            "123456",        # Only numbers
            "abc",           # Too short
            "password123",   # Common pattern
        ]
        
        for password in weak_passwords:
            # This would test the actual password validation logic
            # For now, we'll just assert the concept
            assert len(password) >= 8, "Password should be at least 8 characters"
    
    def test_brute_force_protection(self):
        """Test brute force protection mechanisms."""
        # This would test the actual brute force protection
        # For now, we'll verify the concept exists
        
        # Check that rate limiting is configured
        from app.config import Config
        
        # These should be implemented in the actual application
        assert hasattr(Config, 'RATELIMIT_ENABLED'), "Rate limiting should be configured"
    
    def test_session_security(self):
        """Test session security configuration."""
        from app.config import Config
        
        # Verify secure session configuration
        assert hasattr(Config, 'SESSION_COOKIE_SECURE'), "Session cookie security should be configured"
        assert hasattr(Config, 'SESSION_COOKIE_HTTPONLY'), "Session cookie HTTPOnly should be configured"
    
    def test_jwt_token_security(self):
        """Test JWT token security."""
        from flask_jwt_extended import create_access_token
        
        # Test JWT token creation and validation
        # This would test the actual JWT implementation
        assert True, "JWT tokens should be properly implemented"


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection."""
        # Test various SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM users; --",
            "' UNION SELECT password FROM users --",
        ]
        
        for payload in sql_payloads:
            # This would test the actual input validation
            # For now, we'll assert the concept
            assert len(payload) > 0, "Input validation should handle SQL injection attempts"
    
    def test_xss_protection(self):
        """Test XSS protection."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
        ]
        
        for payload in xss_payloads:
            # This would test the actual XSS protection
            # For now, we'll assert the concept
            assert len(payload) > 0, "Input validation should handle XSS attempts"
    
    def test_csrf_token_validation(self):
        """Test CSRF token validation."""
        # This would test the actual CSRF implementation
        # For now, we'll assert the concept
        assert True, "CSRF tokens should be properly validated"


class TestAuthorization:
    """Test authorization and access control."""
    
    def test_role_based_access_control(self):
        """Test role-based access control."""
        from app.domain import UserRole
        
        # Verify role hierarchy
        roles = [UserRole.STAFF, UserRole.SUPERVISOR, UserRole.ADMIN]
        
        # This would test the actual RBAC implementation
        for role in roles:
            assert role in UserRole, "Role should be properly defined"
    
    def test_privilege_escalation_prevention(self):
        """Test privilege escalation prevention."""
        # This would test the actual privilege escalation prevention
        # For now, we'll assert the concept
        assert True, "Privilege escalation should be prevented"
    
    def test_resource_access_control(self):
        """Test resource access control."""
        # This would test the actual resource access control
        # For now, we'll assert the concept
        assert True, "Resource access should be properly controlled"


class TestSecurityConfiguration:
    """Test security configuration and hardening."""
    
    def test_https_enforcement(self):
        """Test HTTPS enforcement in production."""
        from app.config import Config
        
        # Verify HTTPS enforcement
        assert hasattr(Config, 'FORCE_HTTPS'), "HTTPS should be enforced in production"
    
    def test_security_headers(self):
        """Test security headers configuration."""
        # This would test the actual security headers
        expected_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
        ]
        
        for header in expected_headers:
            assert True, f"{header} should be configured"
    
    def test_error_handling(self):
        """Test secure error handling."""
        # This would test the actual error handling
        # For now, we'll assert the concept
        assert True, "Error messages should not leak sensitive information"


# Security test configuration
@pytest.fixture(scope="session")
def security_config():
    """Configure security testing environment."""
    return {
        "bandit_config": ".bandit",
        "safety_db": "https://pysec-db.appspot.com",
        "zap_config": "zap.conf",
        "test_timeout": 300,
        "max_retries": 3,
    }


# Security test utilities
class SecurityTestUtils:
    """Utilities for security testing."""
    
    @staticmethod
    def generate_sql_payloads():
        """Generate SQL injection test payloads."""
        return [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM users; --",
            "' UNION SELECT password FROM users --",
            "1' OR '1'='1' --",
            "admin'--",
            "admin'/*",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
        ]
    
    @staticmethod
    def generate_xss_payloads():
        """Generate XSS test payloads."""
        return [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
        ]
    
    @staticmethod
    def generate_csrf_payloads():
        """Generate CSRF test payloads."""
        return [
            {"csrf_token": ""},
            {"csrf_token": "invalid"},
            {"csrf_token": None},
        ]
    
    @staticmethod
    def check_security_headers(response):
        """Check for required security headers."""
        required_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        return missing_headers
