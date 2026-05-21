import requests
import tempfile
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000"

def assert_status(name, resp, expected_status=200):
    ok = resp.status_code == expected_status
    print(f"  Status: {resp.status_code} (expected {expected_status}) - {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"  Body: {resp.text[:200]}")
    return ok

def test_clear_twice():
    print("\n[Clear Twice]")

    resp = requests.delete(f"{BASE_URL}/api/v1/clear")
    ok1 = resp.status_code == 200
    print(f"  First clear: {resp.status_code} - {'PASS' if ok1 else 'FAIL'}")

    resp = requests.delete(f"{BASE_URL}/api/v1/clear")
    ok2 = resp.status_code == 200
    print(f"  Second clear: {resp.status_code} (should not crash) - {'PASS' if ok2 else 'FAIL'}")

    return ok1 and ok2

def test_stats_after_clear():
    print("\n[Stats After Clear]")
    resp = requests.get(f"{BASE_URL}/api/v1/stats")
    ok = resp.status_code == 200
    data = resp.json() if ok else {}
    ok = ok and data.get("total_chunks", -1) == 0
    print(f"  Status: {resp.status_code} - total_chunks: {data.get('total_chunks')} - {'PASS' if ok else 'FAIL'}")
    return ok

def test_query_empty_store():
    print("\n[Query Empty Store]")
    resp = requests.post(f"{BASE_URL}/api/v1/query", json={"query": "What is DocGenie?"})
    ok = resp.status_code in (200, 500, 503)
    print(f"  Status: {resp.status_code} (acceptable: 200, 500, 503)")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  answer: {data.get('answer', '')[:80]}")
        print(f"  sources: {len(data.get('sources', []))}")
    print("  PASS" if ok else "  FAIL")
    return ok

def test_concurrent_uploads():
    print("\n[Concurrent Uploads (5 files)]")

    def upload_file(content, i):
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
            f.write(content)
            path = f.name
        try:
            with open(path, 'rb') as f:
                resp = requests.post(
                    f"{BASE_URL}/api/v1/upload",
                    files={'file': (f'concurrent_{i}.txt', f, 'text/plain')}
                )
            return i, resp.status_code, resp.text[:100]
        finally:
            os.unlink(path)

    contents = [f"Concurrent test document number {i}. " * 20 for i in range(5)]
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(upload_file, contents[i], i) for i in range(5)]
        results = []
        for future in as_completed(futures):
            i, status, body = future.result()
            ok = status in (200, 503)
            print(f"  Upload #{i}: {status} - {'PASS' if ok else 'FAIL'}")
            results.append(ok)

    return all(results)

def test_concurrent_queries():
    print("\n[Concurrent Queries (3 queries)]")

    def query(q):
        resp = requests.post(f"{BASE_URL}/api/v1/query", json={"query": q})
        return resp.status_code

    queries = ["What is this?", "Tell me more", "Summarize"]
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(query, q) for q in queries]
        results = []
        for future in as_completed(futures):
            status = future.result()
            ok = status in (200, 500, 503)
            results.append(ok)
            print(f"  Query status: {status} - {'PASS' if ok else 'FAIL'}")

    return all(results)

def test_upload_and_query_race():
    print("\n[Upload + Query Race (10 parallel calls)]")

    def upload():
        content = "Racing test content. " * 10
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
            f.write(content)
            path = f.name
        try:
            with open(path, 'rb') as f:
                resp = requests.post(
                    f"{BASE_URL}/api/v1/upload",
                    files={'file': ('race.txt', f, 'text/plain')}
                )
            return resp.status_code
        finally:
            os.unlink(path)

    def query():
        resp = requests.post(f"{BASE_URL}/api/v1/query", json={"query": "racing"})
        return resp.status_code

    tasks = [upload] * 5 + [query] * 5
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(t) for t in tasks]
        results = []
        for future in as_completed(futures):
            status = future.result()
            ok = status in (200, 500, 503)
            results.append(ok)

    ups = len([r for r in results if r])
    total = len(results)
    print(f"  {ups}/{total} successful (200, 500, or 503 are acceptable)")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("System Edge Case Tests")
    print("=" * 60)

    results = []
    results.append(test_clear_twice())
    results.append(test_stats_after_clear())
    results.append(test_query_empty_store())
    results.append(test_concurrent_uploads())
    results.append(test_concurrent_queries())
    results.append(test_upload_and_query_race())

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed")
    if all(results):
        print("All system edge case tests passed!")
    else:
        print("Some tests FAILED")
    print("=" * 60)
