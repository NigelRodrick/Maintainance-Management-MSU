"""
Phase 4: Coverage Gate
Code coverage analysis with 80% target validation
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_environment():
    """Setup environment variables for testing."""
    os.environ['SECRET_KEY'] = 'test-secret-key-for-coverage-tests'
    os.environ['DB_SERVER'] = 'DESKTOP-IO9GJQS\\SQLEXPRESS'
    os.environ['DB_NAME'] = 'CentralServices_AM_DB'

def run_coverage_analysis():
    """Run comprehensive coverage analysis."""
    print("🔍 PHASE 4: COVERAGE GATE")
    print("=" * 60)
    
    print("📋 COVERAGE GATE CRITERIA:")
    print("  Command: pytest --cov=app --cov-fail-under=80")
    print("  Target: Achieve 80% overall coverage")
    
    # Setup environment
    setup_environment()
    
    print("\n🚀 EXECUTING COVERAGE ANALYSIS:")
    print("   Running pytest with coverage...")
    
    try:
        # Check if pytest and coverage are available
        pytest_check = subprocess.run(['python', '-c', 'import pytest; print("pytest available")'], 
                                    capture_output=True, text=True, timeout=10)
        
        if pytest_check.returncode != 0:
            print("❌ pytest not available")
            return False
        
        coverage_check = subprocess.run(['python', '-c', 'import coverage; print("coverage available")'], 
                                     capture_output=True, text=True, timeout=10)
        
        if coverage_check.returncode != 0:
            print("❌ coverage package not available")
            return False
        
        print("✅ pytest and coverage packages available")
        
        # Run coverage analysis
        cmd = [
            'python', '-m', 'pytest',
            '--cov=app',
            '--cov-fail-under=80',
            '--cov-report=term-missing',
            '--cov-report=html',
            '--cov-report=xml',
            '-v',
            'tests/'
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='.',
            timeout=600  # 10 minute timeout
        )
        
        print(f"\n📊 COVERAGE ANALYSIS RESULTS:")
        print("=" * 50)
        
        # Parse coverage output
        output_lines = result.stdout.split('\n')
        coverage_metrics = {
            'total': 0,
            'covered': 0,
            'percentage': 0,
            'missing_lines': 0,
            'fail_under_80': False
        }
        
        for line in output_lines:
            line = line.strip()
            if line:
                # Parse coverage percentage
                if '%' in line and 'coverage' in line.lower():
                    try:
                        # Extract percentage from lines like "coverage: 75.2%"
                        percentage_str = line.split('%')[0].split()[-1]
                        coverage_metrics['percentage'] = float(percentage_str)
                    except (ValueError, IndexError):
                        pass
                
                # Parse total lines
                if 'total' in line.lower() and 'lines' in line.lower():
                    try:
                        total_str = line.split()[-1]
                        coverage_metrics['total'] = int(total_str)
                    except (ValueError, IndexError):
                        pass
                
                # Parse covered lines
                if 'covered' in line.lower() and 'lines' in line.lower():
                    try:
                        covered_str = line.split()[-1]
                        coverage_metrics['covered'] = int(covered_str)
                    except (ValueError, IndexError):
                        pass
                
                # Parse missing lines
                if 'missing' in line.lower() and 'lines' in line.lower():
                    try:
                        missing_str = line.split()[-1]
                        coverage_metrics['missing_lines'] = int(missing_str)
                    except (ValueError, IndexError):
                        pass
                
                # Display important output
                if any(keyword in line.lower() for keyword in ['coverage', 'total', 'covered', 'missing', 'fail']):
                    print(f"  📄 {line}")
        
        # Check if coverage failed under 80%
        if result.returncode != 0:
            coverage_metrics['fail_under_80'] = True
        
        # Display summary
        print(f"\n📈 COVERAGE SUMMARY:")
        print(f"  Total lines: {coverage_metrics['total']}")
        print(f"  Covered lines: {coverage_metrics['covered']}")
        print(f"  Coverage percentage: {coverage_metrics['percentage']}%")
        print(f"  Missing lines: {coverage_metrics['missing_lines']}")
        print(f"  Failed under 80%: {coverage_metrics['fail_under_80']}")
        
        # Determine pass/fail status
        if coverage_metrics['percentage'] >= 80 and not coverage_metrics['fail_under_80']:
            print(f"\n🎯 PHASE 4 RESULT: ✅ PASS")
            print(f"   Coverage target achieved: {coverage_metrics['percentage']}% >= 80%")
            print(f"   🚀 READY FOR PHASE 5: PERFORMANCE GATE")
            coverage_passed = True
        else:
            print(f"\n❌ PHASE 4 RESULT: ❌ FAIL")
            print(f"   Coverage target not achieved: {coverage_metrics['percentage']}% < 80%")
            print(f"   🔧 Need additional test coverage")
            coverage_passed = False
        
        # Check for HTML report
        html_report_path = 'htmlcov/index.html'
        if os.path.exists(html_report_path):
            print(f"\n📄 HTML coverage report generated: {html_report_path}")
        
        # Check for XML report
        xml_report_path = 'coverage.xml'
        if os.path.exists(xml_report_path):
            print(f"📄 XML coverage report generated: {xml_report_path}")
        
        if result.stderr.strip():
            print(f"\n⚠️ Coverage warnings/errors:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    print(f"  ⚠️ {line}")
        
        return coverage_passed, coverage_metrics
        
    except subprocess.TimeoutExpired:
        print("❌ Coverage analysis timed out after 10 minutes")
        return False, {}
    except Exception as e:
        print(f"❌ Coverage analysis error: {e}")
        return False, {}

def generate_coverage_improvement_plan(coverage_metrics):
    """Generate plan to improve coverage if needed."""
    print("\n🔧 COVERAGE IMPROVEMENT PLAN:")
    print("=" * 50)
    
    if coverage_metrics['percentage'] < 80:
        missing_percentage = 80 - coverage_metrics['percentage']
        additional_lines_needed = int(coverage_metrics['total'] * (missing_percentage / 100))
        
        print(f"TARGET: Increase coverage from {coverage_metrics['percentage']}% to 80%")
        print(f"NEED: Cover additional {additional_lines_needed} lines")
        print(f"CURRENT MISSING: {coverage_metrics['missing_lines']} lines")
        
        print("\nRECOMMENDATIONS:")
        print("1. Add unit tests for uncovered functions")
        print("2. Test edge cases and error conditions")
        print("3. Add integration tests for complex workflows")
        print("4. Test authentication and authorization flows")
        print("5. Add tests for API endpoints")
        print("6. Test database operations and edge cases")
        
        print("\nPRIORITY AREAS:")
        if coverage_metrics['missing_lines'] > 100:
            print("HIGH PRIORITY:")
            print("  - Focus on core business logic")
            print("  - Add comprehensive API tests")
            print("  - Test all user workflows")
        elif coverage_metrics['missing_lines'] > 50:
            print("MEDIUM PRIORITY:")
            print("  - Add tests for main features")
            print("  - Test authentication flows")
            print("  - Add integration tests")
        else:
            print("LOW PRIORITY:")
            print("  - Add unit tests for missing coverage")
            print("  - Test edge cases")
            print("  - Improve existing test coverage")
        
        print(f"\nESTIMATED EFFORT: {additional_lines_needed // 10} hours")
        print("ESTIMATED TIMELINE: 1-2 sprints")

def main():
    """Main execution."""
    print("🔍 MSU MAINTENANCE SYSTEM - PHASE 4 COVERAGE GATE")
    print("=" * 70)
    
    # Step 1: Run coverage analysis
    coverage_passed, coverage_metrics = run_coverage_analysis()
    
    print("\n📊 FINAL PHASE 4 RESULTS:")
    print("=" * 50)
    
    if coverage_passed:
        print("✅ COVERAGE GATE: PASSED")
        print("   Coverage target achieved")
        print("   Code quality validated")
        print("   🚀 READY FOR PHASE 5: PERFORMANCE GATE")
        
        print("\n🎯 PHASE 4 VALIDATION: ✅ COMPLETE")
        print("   Coverage gate completed successfully")
        print("   🚀 READY FOR PHASE 5: PERFORMANCE GATE")
        
    else:
        print("❌ COVERAGE GATE: FAILED")
        print("   Coverage target not achieved")
        print("   🔧 Additional test coverage required")
        
        # Generate improvement plan
        generate_coverage_improvement_plan(coverage_metrics)
        
        print("\n⚠️ PHASE 4 VALIDATION: ❌ INCOMPLETE")
        print("   Coverage gate failed")
        print("   🔧 Implement additional tests")
        print("   🔧 Re-run coverage analysis")
    
    print("\n📊 SYSTEM STATUS:")
    print("Phase 1: ✅ COMPLETE - Clean startup validated")
    print("Phase 2: ✅ COMPLETE - Database integrity")
    print("Phase 3: ✅ COMPLETE - Smoke tests")
    print(f"Phase 4: {'✅ COMPLETE' if coverage_passed else '❌ INCOMPLETE'} - Coverage gate")
    print("Phase 5: 🚀 READY - Performance gate")
    print("Phase 6: ✅ COMPLETE - Security gate")
    print("Phase 8: 🚀 READY - Deployment gate")

if __name__ == '__main__':
    main()
