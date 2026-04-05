"""
Phase 4: Coverage Gate Validation
Validates code coverage meets the >= 80% requirement
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def run_coverage_validation():
    """Run pytest with coverage analysis."""
    print("📊 Phase 4: Coverage Gate Validation")
    print("=" * 60)
    
    print("\n🔍 Running Coverage Analysis")
    print("Target: >= 80% overall coverage")
    print("Focus: Services, repositories, API layers")
    print()
    
    try:
        # Coverage command from testing strategy
        cmd = [
            'python', '-m', 'pytest',
            '--cov=app',
            '--cov-fail-under=80',
            '--cov-report=term-missing',
            '--cov-report=html',
            '--cov-report=xml',
            '-v',
            '--tb=short',
            'tests/'  # Run all tests in tests directory
        ]
        
        print(f"🚀 Executing: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        print("\n📊 COVERAGE RESULTS:")
        print("=" * 50)
        
        if result.returncode == 0:
            print("✅ Coverage analysis completed successfully")
            
            # Parse and display key results
            output_lines = result.stdout.split('\n')
            
            for line in output_lines:
                line = line.strip()
                if line:
                    print(f"  {line}")
            
            # Look for coverage summary
            if 'coverage:' in result.stdout.lower():
                print("\n📈 Coverage information found")
                print("📊 Coverage report generated")
                print("📄 HTML report created in htmlcov/")
                print("📄 XML report created for CI/CD integration")
            
            print("\n🎯 PHASE 4 RESULT: ✅ PASS")
            print("   Coverage gate validation completed")
            print("   🚀 READY FOR PHASE 5: PERFORMANCE GATE")
            return True
            
        else:
            print(f"❌ Coverage analysis failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error during coverage analysis: {e}")
        return False

def check_coverage_reports():
    """Check if coverage reports were generated."""
    print("\n📁 Checking Coverage Reports")
    
    reports = []
    
    # Check for HTML report
    if os.path.exists('htmlcov/index.html'):
        reports.append("✅ HTML coverage report: htmlcov/index.html")
        print("✅ HTML coverage report found")
    else:
        print("⚠️ HTML coverage report not found")
    
    # Check for XML report
    if os.path.exists('coverage.xml'):
        reports.append("✅ XML coverage report: coverage.xml")
        print("✅ XML coverage report found")
    else:
        print("⚠️ XML coverage report not found")
    
    # Check for .coverage file
    if os.path.exists('.coverage'):
        reports.append("✅ Coverage data file: .coverage")
        print("✅ Coverage data file found")
    else:
        print("⚠️ Coverage data file not found")
    
    return len(reports) == 3

def main():
    """Main execution."""
    print("🎯 MSU MAINTENANCE SYSTEM - PHASE 4 COVERAGE GATE")
    print("=" * 70)
    
    print("\n📋 COVERAGE GATE CRITERIA:")
    print("  Command: pytest --cov=app --cov-fail-under=80")
    print("  Target: >= 80% overall coverage")
    print("  Focus: Services, repositories, API layers")
    print("  Output: Coverage reports (HTML, XML, data)")
    
    # Step 1: Run coverage validation
    if run_coverage_validation():
        print("\n✅ Coverage validation completed")
        
        # Step 2: Check for reports
        reports_complete = check_coverage_reports()
        
        print("\n📊 REPORTS STATUS:")
        for report in reports_complete:
            print(f"  {report}")
        
        if reports_complete:
            print("\n🎯 PHASE 4 RESULT: ✅ COMPLETE")
            print("   Coverage gate passed successfully")
            print("   📊 Coverage reports generated")
            print("   🚀 READY FOR PHASE 5: PERFORMANCE GATE")
            
            print("\n📈 NEXT STEPS:")
            print("1. PERFORMANCE GATE (Phase 5):")
            print("   → Command: pytest tests/performance/")
            print("   → Tool: Locust or Apache Benchmarks")
            print("   → Target: P95 response time < 500ms at 50 concurrent users")
            print("   → Metrics: Response time, throughput, error rates")
            
            print("\n2. SECURITY GATE (Phase 6):")
            print("   → Static analysis: bandit -r app/ -ll")
            print("   → Dependency audit: pip-audit -r requirements.txt")
            print("   → Target: Zero HIGH severity findings")
            print("   → Target: Zero CRITICAL/HIGH vulnerabilities")
            
            print("\n3. DEPLOYMENT GATE (Phase 8):")
            print("   → Command: docker compose up --build (staging)")
            print("   → Pipeline: GitHub Actions CI/CD")
            print("   → Target: All containers healthy, pipeline green")
            print("   → Final: UAT sign-off from MSU stakeholder")
            
        else:
            print("\n⚠️ PHASE 4 RESULT: ❌ INCOMPLETE")
            print("   Coverage validation failed")
            print("   🔧 Review coverage analysis results")
            print("   → Re-run coverage gate after fixes")
    else:
        print("\n❌ Coverage validation failed")
        print("🔧 Review test configuration and dependencies")

if __name__ == '__main__':
    main()
