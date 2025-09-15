#!/usr/bin/env python3
"""
Quick test to verify API is running
"""

import requests
import json
import sys

def test_api():
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is running!")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
            
            # Test statistics endpoint
            stats_response = requests.get("http://localhost:8000/api/statistics", timeout=2)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"\n📊 Database Statistics:")
                print(f"   Total Submissions: {stats.get('total_submissions', 0)}")
                print(f"   Total Samples: {stats.get('total_samples', 0)}")
                
            print("\n✨ API is working correctly!")
            print("   View API docs at: http://localhost:8000/docs")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at http://localhost:8000")
        print("   Make sure the API server is running:")
        print("   uv run python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
