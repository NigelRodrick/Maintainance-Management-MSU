"""
Test Execution Script
Runs all test suites with proper configuration and reporting.
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path


class TestRunner:
    """Comprehensive test runner for MSU Maintenance System."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}
        self.start_time = time.time()
    
    def run_unit_tests(self):
        """Run unit tests with coverage."""
        print("🧪 Running Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-m", "unit",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=xml",
            "--cov-report=term-missing",
            "--cov-fail-under=90",  # 90% coverage for unit tests
            "--junit-xml=test-results/unit-tests.xml",
            "-v"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["unit_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "coverage_file": "htmlcov/index.html",
            "junit_file": "test-results/unit-tests.xml"
        }
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
        else:
            print("❌ Unit tests failed")
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_integration_tests(self):
        """Run integration tests."""
        print("🔗 Running Integration Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-m", "integration",
            "--cov=app",
            "--cov-report=html:integration-coverage",
            "--cov-report=xml:integration-coverage.xml",
            "--cov-fail-under=80",  # 80% coverage for integration tests
            "--junit-xml=test-results/integration-tests.xml",
            "-v"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["integration_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "coverage_file": "integration-coverage/index.html",
            "junit_file": "test-results/integration-tests.xml"
        }
        
        if result.returncode == 0:
            print("✅ Integration tests passed")
        else:
            print("❌ Integration tests failed")
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_e2e_tests(self):
        """Run end-to-end tests with Playwright."""
        print("🎭 Running End-to-End Tests...")
        
        # Install Playwright browsers if needed
        install_cmd = ["python", "-m", "playwright", "install", "chromium"]
        subprocess.run(install_cmd, cwd=self.project_root, capture_output=True)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/e2e/",
            "-m", "e2e",
            "--browser", "chromium",
            "--headed",  # Set to False for headless mode
            "--screenshot=only-on-failure",
            "--video=retain-on-failure",
            "--junit-xml=test-results/e2e-tests.xml",
            "-v"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["e2e_tests"] = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "junit_file": "test-results/e2e-tests.xml",
            "screenshots": "test-results/screenshots",
            "videos": "test-results/videos"
        }
        
        if result.returncode == 0:
            print("✅ E2E tests passed")
        else:
            print("❌ E2E tests failed")
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_security_tests(self):
        """Run security tests."""
        print("🔒 Running Security Tests...")
        
        # Run Bandit static analysis
        print("  Running Bandit static analysis...")
        bandit_cmd = [
            "bandit",
            "-r", "app/",
            "-f", "json",
            "-o", "test-results/bandit-report.json",
            "-f", "text",
            "-o", "test-results/bandit-report.txt"
        ]
        
        bandit_result = subprocess.run(bandit_cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Run Safety dependency check
        print("  Running Safety dependency check...")
        safety_cmd = [
            "safety",
            "check",
            "--json",
            "--output", "test-results/safety-report.json",
            "--output", "test-results/safety-report.txt"
        ]
        
        safety_result = subprocess.run(safety_cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Run pytest security tests
        print("  Running pytest security tests...")
        security_test_cmd = [
            "python", "-m", "pytest",
            "tests/security/",
            "--junit-xml=test-results/security-tests.xml",
            "-v"
        ]
        
        security_test_result = subprocess.run(security_test_cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Analyze results
        bandit_passed = bandit_result.returncode == 0
        safety_passed = safety_result.returncode == 0
        security_tests_passed = security_test_result.returncode == 0
        
        self.test_results["security_tests"] = {
            "bandit": {
                "exit_code": bandit_result.returncode,
                "report_file": "test-results/bandit-report.json"
            },
            "safety": {
                "exit_code": safety_result.returncode,
                "report_file": "test-results/safety-report.json"
            },
            "security_tests": {
                "exit_code": security_test_result.returncode,
                "junit_file": "test-results/security-tests.xml"
            }
        }
        
        if bandit_passed and safety_passed and security_tests_passed:
            print("✅ Security tests passed")
        else:
            print("❌ Security tests failed")
            if not bandit_passed:
                print("  Bandit issues found")
            if not safety_passed:
                print("  Safety issues found")
            if not security_tests_passed:
                print("  Security test failures")
        
        return bandit_passed and safety_passed and security_tests_passed
    
    def run_performance_tests(self):
        """Run performance tests."""
        print("⚡ Running Performance Tests...")
        
        # Run pytest performance tests
        cmd = [
            "python", "-m", "pytest",
            "tests/e2e/test_critical_journeys_enhanced.py::TestPerformance",
            "--junit-xml=test-results/performance-tests.xml",
            "-v"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        self.test_results["performance_tests"] = {
            "exit_code": result.returncode,
            "junit_file": "test-results/performance-tests.xml"
        }
        
        if result.returncode == 0:
            print("✅ Performance tests passed")
        else:
            print("❌ Performance tests failed")
            print(result.stderr)
        
        return result.returncode == 0
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("📊 Generating Test Report...")
        
        # Create test results directory
        test_results_dir = self.project_root / "test-results"
        test_results_dir.mkdir(exist_ok=True)
        
        # Calculate total execution time
        total_time = time.time() - self.start_time
        
        # Generate HTML report
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MSU Maintenance System - Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .summary-item {{ flex: 1; padding: 15px; border-radius: 5px; text-align: center; }}
                .total-time {{ font-size: 18px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MSU Maintenance System - Test Report</h1>
                <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p class="total-time">Total Execution Time: {total_time:.2f} seconds</p>
            </div>
            
            <div class="summary">
                <div class="summary-item passed">
                    <h3>Unit Tests</h3>
                    <p>{'✅ Passed' if self.test_results.get('unit_tests', {}).get('exit_code') == 0 else '❌ Failed'}</p>
                </div>
                <div class="summary-item passed">
                    <h3>Integration Tests</h3>
                    <p>{'✅ Passed' if self.test_results.get('integration_tests', {}).get('exit_code') == 0 else '❌ Failed'}</p>
                </div>
                <div class="summary-item passed">
                    <h3>E2E Tests</h3>
                    <p>{'✅ Passed' if self.test_results.get('e2e_tests', {}).get('exit_code') == 0 else '❌ Failed'}</p>
                </div>
                <div class="summary-item passed">
                    <h3>Security Tests</h3>
                    <p>{'✅ Passed' if self.test_results.get('security_tests', {}).get('bandit', {}).get('exit_code') == 0 else '❌ Failed'}</p>
                </div>
            </div>
        """
        
        # Add detailed sections for each test type
        for test_type, results in self.test_results.items():
            status = "passed" if results.get("exit_code") == 0 else "failed"
            report_html += f"""
            <div class="test-section {status}">
                <h2>{test_type.replace('_', ' ').title()}</h2>
                <p>Status: {'✅ Passed' if results.get('exit_code') == 0 else '❌ Failed'}</p>
        """
            
            # Add links to reports
            if "coverage_file" in results:
                report_html += f'<p><a href="{results["coverage_file"]}">Coverage Report</a></p>'
            
            if "junit_file" in results:
                report_html += f'<p><a href="{results["junit_file"]}">JUnit XML Report</a></p>'
            
            if "report_file" in results:
                report_html += f'<p><a href="{results["report_file"]}">Security Report</a></p>'
            
            report_html += "</div>"
        
        report_html += """
        </body>
        </html>
        """
        
        # Save report
        report_file = test_results_dir / "test-report.html"
        with open(report_file, 'w') as f:
            f.write(report_html)
        
        print(f"✅ Test report generated: {report_file}")
        
        # Save results as JSON
        json_file = test_results_dir / "test-results.json"
        with open(json_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"✅ Test results saved: {json_file}")
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Starting Comprehensive Test Suite...")
        print("=" * 50)
        
        # Create test results directory
        test_results_dir = self.project_root / "test-results"
        test_results_dir.mkdir(exist_ok=True)
        
        # Run all test suites
        results = {
            "unit": self.run_unit_tests(),
            "integration": self.run_integration_tests(),
            "e2e": self.run_e2e_tests(),
            "security": self.run_security_tests(),
            "performance": self.run_performance_tests()
        }
        
        # Generate report
        self.generate_test_report()
        
        # Print summary
        print("\n" + "=" * 50)
        print("🏁 Test Suite Summary")
        print("=" * 50)
        
        all_passed = True
        for test_type, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_type.title():<15}: {status}")
            if not passed:
                all_passed = False
        
        print("=" * 50)
        
        if all_passed:
            print("🎉 All tests passed! System is ready for deployment.")
            return 0
        else:
            print("⚠️  Some tests failed. Please review the reports.")
            return 1


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run MSU Maintenance System test suite")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.unit:
        success = runner.run_unit_tests()
    elif args.integration:
        success = runner.run_integration_tests()
    elif args.e2e:
        success = runner.run_e2e_tests()
    elif args.security:
        success = runner.run_security_tests()
    elif args.performance:
        success = runner.run_performance_tests()
    else:
        success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
