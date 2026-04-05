#!/usr/bin/env python3
"""
OWASP ZAP Security Scan Script
Automated security scanning for the MSU Maintenance System.
"""

import subprocess
import time
import json
import sys
from pathlib import Path


class ZapSecurityScanner:
    """OWASP ZAP security scanner."""
    
    def __init__(self, target_url: str, zap_host: str = "localhost", zap_port: int = 8080):
        self.target_url = target_url
        self.zap_host = zap_host
        self.zap_port = zap_port
        self.zap_api_url = f"http://{zap_host}:{zap_port}"
        
    def run_zap_scan(self) -> dict:
        """Run complete ZAP security scan."""
        results = {
            'target_url': self.target_url,
            'scan_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'alerts': [],
            'high_risks': 0,
            'medium_risks': 0,
            'low_risks': 0,
            'informational': 0,
            'passed': False
        }
        
        try:
            print(f"Starting ZAP security scan for: {self.target_url}")
            
            # Step 1: Start ZAP spider
            print("Step 1: Starting spider scan...")
            spider_id = self._start_spider()
            if spider_id:
                self._wait_for_spider(spider_id)
            
            # Step 2: Start active scan
            print("Step 2: Starting active scan...")
            scan_id = self._start_active_scan()
            if scan_id:
                self._wait_for_scan(scan_id)
            
            # Step 3: Get alerts
            print("Step 3: Retrieving security alerts...")
            alerts = self._get_alerts()
            results['alerts'] = alerts
            
            # Step 4: Analyze results
            print("Step 4: Analyzing scan results...")
            self._analyze_alerts(alerts, results)
            
            # Step 5: Generate report
            print("Step 5: Generating security report...")
            self._generate_report(results)
            
            # Step 6: Determine pass/fail
            results['passed'] = results['high_risks'] == 0
            
            return results
            
        except Exception as e:
            print(f"Error during ZAP scan: {e}")
            results['error'] = str(e)
            return results
    
    def _start_spider(self) -> str:
        """Start ZAP spider scan."""
        cmd = [
            'curl', '-X', 'POST',
            f'{self.zap_api_url}/JSON/spider/action/scan/',
            '-d', f'url={self.target_url}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('scanId')
            else:
                print(f"Spider start failed: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print("Spider start timed out")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON response from spider: {result.stdout}")
            return None
    
    def _wait_for_spider(self, spider_id: str, timeout: int = 300):
        """Wait for spider scan to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            cmd = [
                'curl', '-X', 'GET',
                f'{self.zap_api_url}/JSON/spider/view/status/',
                '-d', f'scanId={spider_id}'
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    progress = data.get('status', 0)
                    print(f"Spider progress: {progress}%")
                    
                    if progress >= 100:
                        print("Spider scan completed")
                        return True
                
                time.sleep(5)
            except (subprocess.TimeoutExpired, json.JSONDecodeError):
                print("Error checking spider status")
                time.sleep(5)
        
        print("Spider scan timed out")
        return False
    
    def _start_active_scan(self) -> str:
        """Start ZAP active scan."""
        cmd = [
            'curl', '-X', 'POST',
            f'{self.zap_api_url}/JSON/ascan/action/scan/',
            '-d', f'url={self.target_url}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('scanId')
            else:
                print(f"Active scan start failed: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print("Active scan start timed out")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON response from active scan: {result.stdout}")
            return None
    
    def _wait_for_scan(self, scan_id: str, timeout: int = 600):
        """Wait for active scan to complete."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            cmd = [
                'curl', '-X', 'GET',
                f'{self.zap_api_url}/JSON/ascan/view/status/',
                '-d', f'scanId={scan_id}'
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    progress = data.get('status', 0)
                    print(f"Active scan progress: {progress}%")
                    
                    if progress >= 100:
                        print("Active scan completed")
                        return True
                
                time.sleep(10)
            except (subprocess.TimeoutExpired, json.JSONDecodeError):
                print("Error checking scan status")
                time.sleep(10)
        
        print("Active scan timed out")
        return False
    
    def _get_alerts(self) -> list:
        """Get security alerts from ZAP."""
        cmd = [
            'curl', '-X', 'GET',
            f'{self.zap_api_url}/JSON/core/view/alerts/'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('alerts', [])
            else:
                print(f"Failed to get alerts: {result.stderr}")
                return []
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            print("Error getting alerts")
            return []
    
    def _analyze_alerts(self, alerts: list, results: dict):
        """Analyze security alerts and categorize by risk."""
        for alert in alerts:
            risk = alert.get('risk', 'Informational').lower()
            
            if risk == 'high':
                results['high_risks'] += 1
            elif risk == 'medium':
                results['medium_risks'] += 1
            elif risk == 'low':
                results['low_risks'] += 1
            else:
                results['informational'] += 1
    
    def _generate_report(self, results: dict):
        """Generate security scan report."""
        report = {
            'summary': {
                'target_url': results['target_url'],
                'scan_time': results['scan_time'],
                'high_risks': results['high_risks'],
                'medium_risks': results['medium_risks'],
                'low_risks': results['low_risks'],
                'informational': results['informational'],
                'passed': results['passed']
            },
            'alerts': results['alerts']
        }
        
        # Save report to file
        report_file = f"zap_security_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Security report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("SECURITY SCAN SUMMARY")
        print("="*50)
        print(f"Target: {results['target_url']}")
        print(f"High Risk Issues: {results['high_risks']}")
        print(f"Medium Risk Issues: {results['medium_risks']}")
        print(f"Low Risk Issues: {results['low_risks']}")
        print(f"Informational: {results['informational']}")
        print(f"Status: {'PASSED' if results['passed'] else 'FAILED'}")
        print("="*50)


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OWASP ZAP Security Scanner')
    parser.add_argument('--target', required=True, help='Target URL to scan')
    parser.add_argument('--zap-host', default='localhost', help='ZAP server host')
    parser.add_argument('--zap-port', type=int, default=8080, help='ZAP server port')
    
    args = parser.parse_args()
    
    scanner = ZapSecurityScanner(args.target, args.zap_host, args.zap_port)
    results = scanner.run_zap_scan()
    
    # Exit with appropriate code
    sys.exit(0 if results.get('passed', False) else 1)


if __name__ == '__main__':
    main()
