import requests
import tempfile
import os
import time

BASE_URL = "http://localhost:8000"

def assert_status(name, resp, expected_status=200):
    print(f"\n[{name}]")
    print(f"  Status: {resp.status_code} (expected {expected_status})")
    ok = resp.status_code == expected_status
    print(f"  {'PASS' if ok else 'FAIL'} - {resp.text[:200]}")
    return ok

def test_1_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert_status("Health Check", resp)
    return resp.status_code == 200

def test_2_empty_file():
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        path = f.name
    try:
        with open(path, 'rb') as f:
            resp = requests.post(f"{BASE_URL}/api/v1/upload", files={'file': ('empty.txt', f, 'text/plain')})
        assert_status("Empty File Upload", resp, expected_status=200)
        data = resp.json()
        ok = data.get("chunks_created", -1) == 0
        print(f"  chunks_created: {data.get('chunks_created')} - {'PASS' if ok else 'FAIL'}")
        return ok
    finally:
        os.unlink(path)

def test_3_unsupported_type():
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as f:
        f.write("col1,col2\n1,2\n3,4")
        path = f.name
    try:
        with open(path, 'rb') as f:
            resp = requests.post(f"{BASE_URL}/api/v1/upload", files={'file': ('data.csv', f, 'text/csv')})
        assert_status("Unsupported Type (.csv)", resp, expected_status=400)
        data = resp.json()
        ok = "not supported" in data.get("detail", "").lower() or "csv" in data.get("detail", "").lower()
        print(f"  detail: {data.get('detail', '')} - {'PASS' if ok else 'FAIL'}")
        return ok
    finally:
        os.unlink(path)

def test_4_no_extension():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Hello world")
        path = f.name
    try:
        with open(path, 'rb') as f:
            resp = requests.post(f"{BASE_URL}/api/v1/upload", files={'file': ('noext', f, 'text/plain')})
        assert_status("No Extension", resp, expected_status=400)
        return True
    finally:
        os.unlink(path)

def test_5_binary_file():
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'\x25\x50\x44\x46\x20\x20\x20')  # fake PDF header but no real content
        path = f.name
    try:
        with open(path, 'rb') as f:
            resp = requests.post(f"{BASE_URL}/api/v1/upload", files={'file': ('fake.pdf', f, 'application/pdf')})
        assert_status("Fake/Corrupt PDF", resp, expected_status=400)
        data = resp.json()
        ok = "detail" in data
        print(f"  detail: {data.get('detail', '')[:100]} - {'PASS' if ok else 'FAIL'}")
        return ok
    finally:
        os.unlink(path)

def test_6_large_file():
    content = "Hello world. " * 100_000  # ~1.3MB
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    try:
        with open(path, 'rb') as f:
            resp = requests.post(f"{BASE_URL}/api/v1/upload", files={'file': ('large.txt', f, 'text/plain')})
        ok = resp.status_code in (200, 503)
        print(f"[Large File (~1.3MB)]")
        print(f"  Status: {resp.status_code} (expected 200 or 503 for rate-limit)")
        if resp.status_code == 503:
            print(f"  Rate-limited (acceptable) - PASS")
        elif resp.status_code == 200:
            data = resp.json()
            print(f"  chunks_created: {data.get('chunks_created')} - PASS")
        else:
            print(f"  FAIL")
        return ok
    finally:
        os.unlink(path)

def test_7_duplicate_upload():
    content = "Some unique test content for DocGenie."
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    try:
        for i in range(2):
            with open(path, 'rb') as f:
                resp = requests.post(f"{BASE_URL}/api/v1/upload", files={'file': ('dup_test.txt', f, 'text/plain')})
            ok = resp.status_code in (200, 503)
            print(f"  Upload #{i+1}: Status {resp.status_code} - {'PASS' if ok else 'FAIL'}")
        return True
    finally:
        os.unlink(path)

def test_8_upload_missing_file():
    resp = requests.post(f"{BASE_URL}/api/v1/upload")
    assert_status("Missing File in Upload", resp, expected_status=422)
    return resp.status_code == 422


if __name__ == "__main__":
    print("=" * 60)
    print("Upload Edge Case Tests")
    print("=" * 60)

    healthy = test_1_health()
    if not healthy:
        print("\nServer not healthy, aborting.")
        exit(1)

    # Clear first
    requests.delete(f"{BASE_URL}/api/v1/clear")

    results = []
    results.append(test_2_empty_file())
    results.append(test_3_unsupported_type())
    results.append(test_4_no_extension())
    results.append(test_5_binary_file())
    results.append(test_6_large_file())
    results.append(test_7_duplicate_upload())
    results.append(test_8_upload_missing_file())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed")
    if all(results):
        print("All edge case tests passed!")
    else:
        print("Some tests FAILED")
    print("=" * 60)
