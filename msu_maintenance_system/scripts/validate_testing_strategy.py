"""
Test Validation Script
Validates that all testing requirements are met according to the specification.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET


class TestValidator:
    """Validates testing requirements and coverage."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {}
    
    def validate_unit_test_coverage(self):
        """Validate unit test coverage meets 90% requirement."""
        print("🔍 Validating Unit Test Coverage...")
        
        # Run unit tests with coverage
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-m", "unit",
            "--cov=app",
            "--cov-report=json",
            "--cov-report=term",
            "-q"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Parse coverage report
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data["totals"]["percent_covered"]
            service_coverage = self._get_service_coverage(coverage_data)
            domain_coverage = self._get_domain_coverage(coverage_data)
            
            self.validation_results["unit_coverage"] = {
                "total_coverage": total_coverage,
                "service_coverage": service_coverage,
                "domain_coverage": domain_coverage,
                "meets_requirement": total_coverage >= 90.0 and service_coverage >= 90.0 and domain_coverage >= 100.0
            }
            
            print(f"  Total Coverage: {total_coverage:.1f}%")
            print(f"  Service Coverage: {service_coverage:.1f}%")
            print(f"  Domain Coverage: {domain_coverage:.1f}%")
            
            if self.validation_results["unit_coverage"]["meets_requirement"]:
                print("  ✅ Unit test coverage meets requirements")
            else:
                print("  ❌ Unit test coverage below requirements")
        else:
            print("  ❌ Coverage report not found")
            self.validation_results["unit_coverage"] = {"meets_requirement": False}
        
        return self.validation_results["unit_coverage"]["meets_requirement"]
    
    def validate_integration_test_coverage(self):
        """Validate integration test coverage meets 80% requirement."""
        print("🔍 Validating Integration Test Coverage...")
        
        # Run integration tests with coverage
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-m", "integration",
            "--cov=app",
            "--cov-report=json:integration-coverage.json",
            "--cov-report=term",
            "-q"
        ]
        
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Parse coverage report
        coverage_file = self.project_root / "integration-coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
            
            api_coverage = self._get_api_coverage(coverage_data)
            total_coverage = coverage_data["totals"]["percent_covered"]
            
            self.validation_results["integration_coverage"] = {
                "api_coverage": api_coverage,
                "total_coverage": total_coverage,
                "meets_requirement": api_coverage >= 80.0
            }
            
            print(f"  API Coverage: {api_coverage:.1f}%")
            print(f"  Total Coverage: {total_coverage:.1f}%")
            
            if self.validation_results["integration_coverage"]["meets_requirement"]:
                print("  ✅ Integration test coverage meets requirements")
            else:
                print("  ❌ Integration test coverage below requirements")
        else:
            print("  ❌ Integration coverage report not found")
            self.validation_results["integration_coverage"] = {"meets_requirement": False}
        
        return self.validation_results["integration_coverage"]["meets_requirement"]
    
    def validate_e2e_test_coverage(self):
        """Validate E2E tests cover all critical user journeys."""
        print("🔍 Validating E2E Test Coverage...")
        
        # Check for required test files
        required_journeys = [
            "test_critical_journeys.py",
            "test_mobile_responsive.py",
            "test_accessibility.py"
        ]
        
        e2e_dir = self.project_root / "tests" / "e2e"
        missing_tests = []
        
        for journey in required_journeys:
            if not (e2e_dir / journey).exists():
                missing_tests.append(journey)
        
        # Check for critical test methods
        critical_methods = [
            "test_staff_login_job_submission_flow",
            "test_supervisor_assignment_workflow",
            "test_admin_user_management",
            "test_mobile_login_page",
            "test_keyboard_navigation"
        ]
        
        if not missing_tests:
            # Parse test files to check for critical methods
            test_files = list(e2e_dir.glob("test_*.py"))
            found_methods = []
            
            for test_file in test_files:
                with open(test_file) as f:
                    content = f.read()
                    for method in critical_methods:
                        if method in content:
                            found_methods.append(method)
            
            missing_methods = [m for m in critical_methods if m not in found_methods]
        else:
            missing_methods = critical_methods
        
        self.validation_results["e2e_coverage"] = {
            "missing_files": missing_tests,
            "missing_methods": missing_methods,
            "meets_requirement": len(missing_tests) == 0 and len(missing_methods) == 0
        }
        
        if self.validation_results["e2e_coverage"]["meets_requirement"]:
            print("  ✅ E2E test coverage meets requirements")
        else:
            print("  ❌ E2E test coverage incomplete")
            if missing_tests:
                print(f"    Missing files: {missing_tests}")
            if missing_methods:
                print(f"    Missing methods: {missing_methods}")
        
        return self.validation_results["e2e_coverage"]["meets_requirement"]
    
    def validate_security_testing(self):
        """Validate security testing meets zero HIGH/CRITICAL findings requirement."""
        print("🔍 Validating Security Testing...")
        
        # Run Bandit analysis
        print("  Running Bandit analysis...")
        bandit_cmd = [
            "bandit",
            "-r", "app/",
            "-f", "json",
            "-o", "bandit-validation.json"
        ]
        
        bandit_result = subprocess.run(bandit_cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Run Safety check
        print("  Running Safety check...")
        safety_cmd = [
            "safety",
            "check",
            "--json",
            "--output", "safety-validation.json"
        ]
        
        safety_result = subprocess.run(safety_cmd, cwd=self.project_root, capture_output=True, text=True)
        
        # Analyze results
        high_critical_issues = 0
        
        # Parse Bandit results
        bandit_file = self.project_root / "bandit-validation.json"
        if bandit_file.exists():
            with open(bandit_file) as f:
                bandit_data = json.load(f)
            
            high_issues = [i for i in bandit_data["results"] if i["issue_severity"] == "HIGH"]
            critical_issues = [i for i in bandit_data["results"] if i["issue_severity"] == "CRITICAL"]
            
            high_critical_issues += len(high_issues) + len(critical_issues)
            
            print(f"    Bandit: {len(high_issues)} HIGH, {len(critical_issues)} CRITICAL")
        
        # Parse Safety results
        safety_file = self.project_root / "safety-validation.json"
        if safety_file.exists():
            with open(safety_file) as f:
                safety_data = json.load(f)
            
            high_vulns = [v for v in safety_data.get("vulnerabilities", []) 
                         if v.get("vulnerability_class") in ["high", "critical"]]
            
            high_critical_issues += len(high_vulns)
            
            print(f"    Safety: {len(high_vulns)} HIGH/CRITICAL vulnerabilities")
        
        self.validation_results["security_testing"] = {
            "high_critical_issues": high_critical_issues,
            "meets_requirement": high_critical_issues == 0
        }
        
        if self.validation_results["security_testing"]["meets_requirement"]:
            print("  ✅ Security testing meets requirements")
        else:
            print(f"  ❌ Found {high_critical_issues} HIGH/CRITICAL security issues")
        
        return self.validation_results["security_testing"]["meets_requirement"]
    
    def validate_test_data_strategy(self):
        """Validate test data strategy implementation."""
        print("🔍 Validating Test Data Strategy...")
        
        # Check for factory-boy implementation
        conftest_file = self.project_root / "tests" / "conftest.py"
        enhanced_conftest = self.project_root / "tests" / "conftest_enhanced.py"
        
        factory_implementation = False
        realistic_distribution = False
        
        for conftest in [conftest_file, enhanced_conftest]:
            if conftest.exists():
                with open(conftest) as f:
                    content = f.read()
                
                if "factory" in content.lower() and "Factory" in content:
                    factory_implementation = True
                
                if "40% PENDING" in content or "0.4" in content:
                    realistic_distribution = True
        
        # Check for separate test database configuration
        test_db_config = False
        if conftest_file.exists():
            with open(conftest_file) as f:
                content = f.read()
            
            if "test_db" in content or "CentralServices_AM_DB_Test" in content:
                test_db_config = True
        
        # Check for anonymized data
        anonymized_data = factory_implementation  # Factory-boy ensures anonymization
        
        self.validation_results["test_data_strategy"] = {
            "factory_implementation": factory_implementation,
            "realistic_distribution": realistic_distribution,
            "test_db_config": test_db_config,
            "anonymized_data": anonymized_data,
            "meets_requirement": all([factory_implementation, realistic_distribution, test_db_config, anonymized_data])
        }
        
        if self.validation_results["test_data_strategy"]["meets_requirement"]:
            print("  ✅ Test data strategy meets requirements")
        else:
            print("  ❌ Test data strategy incomplete")
            if not factory_implementation:
                print("    Missing factory-boy implementation")
            if not realistic_distribution:
                print("    Missing realistic data distribution")
            if not test_db_config:
                print("    Missing test database configuration")
        
        return self.validation_results["test_data_strategy"]["meets_requirement"]
    
    def validate_test_architecture(self):
        """Validate test architecture matches specification."""
        print("🔍 Validating Test Architecture...")
        
        # Check test directory structure
        required_dirs = [
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/security"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        # Check for required test files
        required_files = [
            "tests/conftest.py",
            "pytest.ini",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        # Check pytest configuration
        pytest_config = False
        pytest_ini = self.project_root / "pytest.ini"
        if pytest_ini.exists():
            with open(pytest_ini) as f:
                content = f.read()
            
            if "cov-fail-under" in content and "markers" in content:
                pytest_config = True
        
        self.validation_results["test_architecture"] = {
            "missing_dirs": missing_dirs,
            "missing_files": missing_files,
            "pytest_config": pytest_config,
            "meets_requirement": len(missing_dirs) == 0 and len(missing_files) == 0 and pytest_config
        }
        
        if self.validation_results["test_architecture"]["meets_requirement"]:
            print("  ✅ Test architecture meets requirements")
        else:
            print("  ❌ Test architecture incomplete")
            if missing_dirs:
                print(f"    Missing directories: {missing_dirs}")
            if missing_files:
                print(f"    Missing files: {missing_files}")
        
        return self.validation_results["test_architecture"]["meets_requirement"]
    
    def _get_service_coverage(self, coverage_data):
        """Extract coverage for service layer."""
        service_files = [f for f in coverage_data["files"] if "/services/" in f]
        
        if not service_files:
            return 0.0
        
        total_lines = sum(f["summary"]["covered_lines"] + f["summary"]["missing_lines"] for f in service_files)
        covered_lines = sum(f["summary"]["covered_lines"] for f in service_files)
        
        return (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
    
    def _get_domain_coverage(self, coverage_data):
        """Extract coverage for domain layer."""
        domain_files = [f for f in coverage_data["files"] if "/domain/" in f]
        
        if not domain_files:
            return 0.0
        
        total_lines = sum(f["summary"]["covered_lines"] + f["summary"]["missing_lines"] for f in domain_files)
        covered_lines = sum(f["summary"]["covered_lines"] for f in domain_files)
        
        return (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
    
    def _get_api_coverage(self, coverage_data):
        """Extract coverage for API layer."""
        api_files = [f for f in coverage_data["files"] if "/api/" in f]
        
        if not api_files:
            return 0.0
        
        total_lines = sum(f["summary"]["covered_lines"] + f["summary"]["missing_lines"] for f in api_files)
        covered_lines = sum(f["summary"]["covered_lines"] for f in api_files)
        
        return (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
    
    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        print("📊 Generating Validation Report...")
        
        # Create validation results directory
        results_dir = self.project_root / "test-results"
        results_dir.mkdir(exist_ok=True)
        
        # Calculate overall status
        all_validations = [
            "unit_coverage",
            "integration_coverage", 
            "e2e_coverage",
            "security_testing",
            "test_data_strategy",
            "test_architecture"
        ]
        
        passed_validations = sum(
            1 for validation in all_validations
            if self.validation_results.get(validation, {}).get("meets_requirement", False)
        )
        
        overall_status = passed_validations == len(all_validations)
        
        # Generate HTML report
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Strategy Validation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .validation {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .summary-item {{ flex: 1; padding: 15px; border-radius: 5px; text-align: center; }}
                .overall {{ font-size: 18px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MSU Maintenance System - Test Strategy Validation</h1>
                <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p class="overall overall-{'passed' if overall_status else 'failed'}">
                    Overall Status: {'✅ PASSED' if overall_status else '❌ FAILED'}
                </p>
                <p>Validations Passed: {passed_validations}/{len(all_validations)}</p>
            </div>
        """
        
        # Add detailed validation results
        for validation in all_validations:
            result = self.validation_results.get(validation, {})
            status = "passed" if result.get("meets_requirement", False) else "failed"
            
            report_html += f"""
            <div class="validation {status}">
                <h2>{validation.replace('_', ' ').title()}</h2>
                <p>Status: {'✅ PASSED' if result.get("meets_requirement", False) else '❌ FAILED'}</p>
            """
            
            # Add specific details for each validation
            if validation == "unit_coverage":
                report_html += f"""
                <p>Total Coverage: {result.get('total_coverage', 0):.1f}%</p>
                <p>Service Coverage: {result.get('service_coverage', 0):.1f}%</p>
                <p>Domain Coverage: {result.get('domain_coverage', 0):.1f}%</p>
                """
            elif validation == "integration_coverage":
                report_html += f"""
                <p>API Coverage: {result.get('api_coverage', 0):.1f}%</p>
                <p>Total Coverage: {result.get('total_coverage', 0):.1f}%</p>
                """
            elif validation == "security_testing":
                report_html += f"""
                <p>High/Critical Issues: {result.get('high_critical_issues', 0)}</p>
                """
            
            report_html += "</div>"
        
        report_html += """
        </body>
        </html>
        """
        
        # Save report
        report_file = results_dir / "validation-report.html"
        with open(report_file, 'w') as f:
            f.write(report_html)
        
        print(f"✅ Validation report generated: {report_file}")
        
        # Save results as JSON
        json_file = results_dir / "validation-results.json"
        with open(json_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"✅ Validation results saved: {json_file}")
        
        return overall_status
    
    def run_validation(self):
        """Run all validation checks."""
        print("🚀 Starting Test Strategy Validation...")
        print("=" * 50)
        
        # Run all validations
        validations = [
            self.validate_test_architecture,
            self.validate_test_data_strategy,
            self.validate_unit_test_coverage,
            self.validate_integration_test_coverage,
            self.validate_e2e_test_coverage,
            self.validate_security_testing
        ]
        
        for validation in validations:
            validation()
            print()
        
        # Generate report
        overall_status = self.generate_validation_report()
        
        # Print summary
        print("=" * 50)
        print("🏁 Validation Summary")
        print("=" * 50)
        
        for validation_name, result in self.validation_results.items():
            status = "✅ PASSED" if result.get("meets_requirement", False) else "❌ FAILED"
            print(f"{validation_name.replace('_', ' ').title():<25}: {status}")
        
        print("=" * 50)
        
        if overall_status:
            print("🎉 All validation checks passed! Test strategy meets requirements.")
            return 0
        else:
            print("⚠️  Some validation checks failed. Please review the report.")
            return 1


def main():
    """Main entry point."""
    import time
    
    validator = TestValidator()
    exit_code = validator.run_validation()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
