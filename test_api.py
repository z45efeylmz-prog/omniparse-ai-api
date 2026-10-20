import asyncio
import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_extract():
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    
    print(f"\n[Test 1] Fetching live webpage: {url}")
    t0 = time.perf_counter()
    resp = client.get(f"/api/v1/extract?url={url}")
    t1 = time.perf_counter()
    
    print(f"Status Code: {resp.status_code}")
    print(f"Total Client Time: {(t1 - t0)*1000:.2f} ms")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Title: {data.get('title')}")
        print(f"Word Count: {data.get('word_count')}")
        print(f"Server Latency: {data.get('latency_ms')} ms")
        print(f"Cached: {data.get('cached')}")
        print(f"Content Preview (first 250 chars):\n{data.get('content')[:250]}...\n")
    else:
        print(f"Error: {resp.text}")

    print("[Test 2] Testing In-Memory Cache (Same URL):")
    t0 = time.perf_counter()
    resp_cached = client.get(f"/api/v1/extract?url={url}")
    t1 = time.perf_counter()
    
    data_cached = resp_cached.json()
    print(f"Total Client Time (Cached): {(t1 - t0)*1000:.2f} ms")
    print(f"Server Latency (Cached): {data_cached.get('latency_ms')} ms")
    print(f"Cached: {data_cached.get('cached')}")

if __name__ == "__main__":
    test_extract()
