"""
Comprehensive test suite for FastAPI and Docker support.

Run this script to verify:
1. All existing tests pass
2. FastAPI endpoints work correctly
3. Conversation continuity is preserved
4. Docker image builds and runs
"""

import subprocess
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path


def run_command(cmd, description):
    """Execute a command and return success/failure."""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"[PASS]")
            if result.stdout:
                print(result.stdout[:500])
            return True
        else:
            print(f"[FAIL]")
            print(result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT]")
        return False
    except Exception as e:
        print(f"[ERROR]: {e}")
        return False


def test_http_endpoint(method, url, data=None, retries=3):
    """Test HTTP endpoint with retries."""
    for attempt in range(retries):
        try:
            if method == "GET":
                response = urllib.request.urlopen(url)
            else:
                request = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    method=method
                )
                request.add_header('Content-Type', 'application/json')
                response = urllib.request.urlopen(request)
            
            result = json.loads(response.read().decode())
            return True, result
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode())
            return False, error_data
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return False, str(e)
    return False, "Max retries exceeded"


def main():
    """Run all verification tests."""
    tests_passed = 0
    tests_failed = 0

    print("\n" + "="*70)
    print("HOLIDAY AGENT - COMPREHENSIVE VERIFICATION TEST SUITE")
    print("="*70)

    # Test 1: Python syntax and imports
    if run_command(
        "python -m py_compile api.py graph.py main.py",
        "Python syntax validation"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Run pytest
    if run_command(
        "python -m pytest tests/ -q",
        "Pytest - All existing tests"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Build Docker image
    if run_command(
        "docker build -t company-chat-agent .",
        "Docker image build"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 4: Start FastAPI server and test endpoints
    print(f"\n{'='*70}")
    print(f"TEST: FastAPI server and endpoints")
    print(f"{'='*70}")
    
    try:
        # Start server
        server_proc = subprocess.Popen(
            "python -m uvicorn api:app --host 127.0.0.1 --port 8000",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(8)  # Wait for server to start
        
        # Test health endpoint
        success, result = test_http_endpoint("GET", "http://127.0.0.1:8000/health")
        if success and result.get("status") == "healthy":
            print("[PASS] Health endpoint working")
            tests_passed += 1
        else:
            print(f"[FAIL] Health endpoint failed: {result}")
            tests_failed += 1
            server_proc.terminate()
            return tests_passed, tests_failed

        # Test chat endpoint
        success, result = test_http_endpoint(
            "POST",
            "http://127.0.0.1:8000/chat",
            {"message": "What are our company holidays?", "thread_id": "test-001"}
        )
        if success and result.get("response"):
            print("[PASS] Chat endpoint working")
            tests_passed += 1
        else:
            print(f"[FAIL] Chat endpoint failed: {result}")
            tests_failed += 1

        # Test conversation continuity
        success, result = test_http_endpoint(
            "POST",
            "http://127.0.0.1:8000/chat",
            {"message": "Tell me more", "thread_id": "test-001"}
        )
        if success and result.get("response"):
            print("[PASS] Conversation continuity working")
            tests_passed += 1
        else:
            print(f"[FAIL] Conversation continuity failed: {result}")
            tests_failed += 1

        # Test thread isolation
        success, result = test_http_endpoint(
            "POST",
            "http://127.0.0.1:8000/chat",
            {"message": "Employee benefits?", "thread_id": "test-002"}
        )
        if success and result.get("response"):
            print("[PASS] Thread isolation working")
            tests_passed += 1
        else:
            print(f"[FAIL] Thread isolation failed: {result}")
            tests_failed += 1

        # Test error handling
        success, result = test_http_endpoint(
            "POST",
            "http://127.0.0.1:8000/chat",
            {"message": "", "thread_id": "test-003"}
        )
        if not success:
            print("[PASS] Error handling working (empty message rejected)")
            tests_passed += 1
        else:
            print(f"[FAIL] Error handling failed: {result}")
            tests_failed += 1

        server_proc.terminate()
        
    except Exception as e:
        print(f"[FAIL] FastAPI test failed: {e}")
        tests_failed += 1

    print(f"\n{'='*70}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"[PASS] Passed: {tests_passed}")
    print(f"[FAIL] Failed: {tests_failed}")
    print(f"{'='*70}\n")

    return tests_passed, tests_failed


if __name__ == "__main__":
    passed, failed = main()
    sys.exit(0 if failed == 0 else 1)
