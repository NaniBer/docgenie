import requests
import tempfile
import os
import time

BASE_URL = "http://localhost:8000"

def test_backend():
    print("=" * 60)
    print("DocGenie Test Suite (single-tenant)")
    print("=" * 60)

    # Test 1: Health Check
    print("\n[1] Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # Test 2: Upload Document
    print("\n[2] Uploading Test Document...")
    test_content = """
    DocGenie Documentation

    DocGenie is an AI-powered chatbot service that allows users to upload documents
    and query them using natural language. It uses RAG (Retrieval-Augmented Generation)
    to provide accurate answers with source attribution.

    Key Features:
    - Document upload (PDF, TXT, MD, DOCX)
    - Vector search using ChromaDB
    - AI-powered responses
    - Source attribution
    """

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name

    try:
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_doc.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")
        os.unlink(temp_file)
        return
    finally:
        os.unlink(temp_file)

    # Test 3: Check Document Stats
    print("\n[3] Checking Document Stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats")
        print(f"Status: {response.status_code}")
        print(f"Stats: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # Test 4: Query Chatbot
    print("\n[4] Querying Chatbot...")
    time.sleep(2)
    try:
        data = {"query": "What is DocGenie?"}
        response = requests.post(f"{BASE_URL}/api/v1/query", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Answer: {result.get('answer')}")
        print(f"Sources: {len(result.get('sources', []))} chunks retrieved")
        print(f"Query Time: {result.get('query_time_ms')}ms")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # Test 5: Clear Documents
    print("\n[5] Clearing Documents...")
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/clear")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed: {e}")
        return

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_backend()
