#!/usr/bin/env python3
"""
Test script to verify the web interface is working
"""

import requests
import time

def test_web_interface():
    """Test all web endpoints"""
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("Testing Resume Evaluator Web Interface")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("/", "Main Page"),
        ("/dashboard", "Dashboard"),
        ("/upload", "Upload Page"),
        ("/api/health", "API Health")
    ]
    
    for endpoint, name in endpoints:
        try:
            print(f"\nTesting {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK (Status: {response.status_code})")
                
                # Check if it's HTML content
                if 'text/html' in response.headers.get('content-type', ''):
                    print(f"   📄 HTML Content: {len(response.text)} characters")
                    if '<html' in response.text.lower():
                        print(f"   ✅ Valid HTML page")
                    else:
                        print(f"   ⚠️  Not a valid HTML page")
                else:
                    print(f"   📊 API Response: {response.text[:100]}...")
            else:
                print(f"❌ {name}: Error (Status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection failed - Is the server running?")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("If all tests show ✅, the web interface is working correctly.")
    print("If you're still seeing folders, try:")
    print("1. Clear browser cache (Ctrl + F5)")
    print("2. Try a different browser")
    print("3. Check the exact URL: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    test_web_interface()
