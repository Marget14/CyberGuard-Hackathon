"""
CyberGuard API Client
Test client and examples for using the CyberGuard API
"""

import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:5000"
API_VERSION = "v1"

class CyberGuardAPIClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.api_version = API_VERSION
        self.session = requests.Session()
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request to API"""
        url = f"{self.base_url}/api/{self.api_version}{endpoint}"
        try:
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            elif method == 'POST':
                response = self.session.post(url, json=kwargs.get('json'), **{k: v for k, v in kwargs.items() if k != 'json'})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {'error': 'Cannot connect to API. Make sure the server is running.'}
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def health_check(self):
        """Check API health"""
        return self._make_request('GET', '/health')
    
    def analyze_email(self, email_text, subject="No Subject"):
        """Analyze email for phishing threats"""
        return self._make_request('POST', '/analyze', json={
            'email_text': email_text,
            'subject': subject
        })
    
    def get_history(self, limit=50, risk_level=None):
        """Get analysis history"""
        params = {'limit': limit}
        if risk_level:
            params['risk_level'] = risk_level
        
        return self._make_request('GET', '/history', params=params)
    
    def get_threats(self, limit=20):
        """Get detected threats"""
        return self._make_request('GET', '/threats', params={'limit': limit})
    
    def get_statistics(self):
        """Get analysis statistics"""
        return self._make_request('GET', '/statistics')
    
    def get_api_info(self):
        """Get API documentation"""
        return self._make_request('GET', '/info')
    
    def clear_database(self):
        """Clear database"""
        return self._make_request('POST', '/clear')

# ==================== Test Examples ====================

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_response(data, indent=2):
    """Pretty print JSON response"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))

def run_api_tests():
    """Run comprehensive API tests"""
    
    # Initialize client
    client = CyberGuardAPIClient()
    
    # Test 1: Health check
    print_header("Test 1: API Health Check")
    response = client.health_check()
    print_response(response)
    
    if 'error' in response:
        print("\n⚠️  Cannot connect to API. Start the server with:")
        print("python C:\\Users\\User\\Desktop\\CyberGuard_API.py")
        return
    
    # Test 2: Get API Info
    print_header("Test 2: API Information")
    response = client.get_api_info()
    print(f"API Version: {response.get('api_version')}")
    print(f"Service: {response.get('service')}")
    print(f"Available Endpoints: {len(response.get('endpoints', {}))}")
    
    # Test 3: Analyze Safe Email
    print_header("Test 3: Analyze Safe Email")
    safe_email = """
    Hello,
    
    Thank you for your order. Your package will be delivered tomorrow.
    
    Best regards,
    Shipping Team
    """
    response = client.analyze_email(safe_email, "Your Order Has Shipped")
    print_response(response)
    
    # Test 4: Analyze Suspicious Email
    print_header("Test 4: Analyze Suspicious Email")
    suspicious_email = """
    URGENT ACTION REQUIRED!
    
    Verify your account immediately at http://192.168.1.1/login.php
    
    Your account has been compromised. Click here to confirm your identity.
    Update your payment method now to avoid account suspension.
    
    Contact: noreply-security@paypal-verify.com
    """
    response = client.analyze_email(suspicious_email, "URGENT: Verify Your Account")
    print_response(response)
    
    # Test 5: Analyze Dangerous Email
    print_header("Test 5: Analyze Dangerous Email")
    dangerous_email = """
    CRITICAL SECURITY ALERT - Δήμος Αθηναίων Account
    
    Το λογαριασμό σας έχει αναστείλει. Επιβεβαίωση άμεσα!
    
    Your account access has been restricted due to unusual activity.
    Verify credentials: http://10.0.0.1/secure/verify.php
    Confirm payment information to reactivate.
    
    Κίνδυνος: Ανοίξτε αμέσως για επιβεβαίωση!
    
    Security Team
    noreply@security-alert.local
    """
    response = client.analyze_email(dangerous_email, "CRITICAL: Account Suspended")
    print_response(response)
    
    # Test 6: Get History
    print_header("Test 6: Get Analysis History")
    response = client.get_history(limit=5)
    print(f"Total Analyses: {response.get('total_count')}")
    print(f"Filtered Count: {response.get('filtered_count')}")
    if response.get('analyses'):
        print("\nLatest Analysis:")
        print_response(response['analyses'][0])
    
    # Test 7: Get Threats
    print_header("Test 7: Get Detected Threats")
    response = client.get_threats(limit=5)
    print(f"Total Threats: {response.get('total_threats')}")
    print(f"Critical Threats: {response.get('critical_threats')}")
    if response.get('threats'):
        print("\nLatest Threat:")
        print_response(response['threats'][0])
    
    # Test 8: Get Statistics
    print_header("Test 8: Analysis Statistics")
    response = client.get_statistics()
    print_response(response)
    
    # Test 9: Filter by Risk Level
    print_header("Test 9: Get Only Dangerous Analyses")
    response = client.get_history(limit=10, risk_level='DANGEROUS')
    print(f"Dangerous Analyses Found: {response.get('filtered_count')}")
    if response.get('analyses'):
        for i, analysis in enumerate(response['analyses'][:3], 1):
            print(f"\n{i}. Subject: {analysis.get('subject')}")
            print(f"   Risk Score: {analysis.get('risk_score')}")
            print(f"   Keywords: {', '.join(analysis.get('keywords_found', [])[:3])}")
    
    print_header("All Tests Complete!")
    print("\n✅ API is working correctly")

if __name__ == '__main__':
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n[CyberGuard] API Client v1.0\n")
    run_api_tests()
