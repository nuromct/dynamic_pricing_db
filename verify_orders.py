from database import execute_query
from main import app
from fastapi.testclient import TestClient
import json

# 1. Check Order Count
count = execute_query('SELECT COUNT(*) as count FROM "Order"')[0]['count']
print(f"Total Orders in DB: {count}")

# 2. Test Pagination API
client = TestClient(app)
response = client.get("/api/orders?page=1&limit=5")
data = response.json()

print(f"API Response Status: {response.status_code}")
if response.status_code == 200:
    print(f"Keys in response: {list(data.keys())}")
    print(f"Orders returned: {len(data['orders'])}")
    print(f"Total metadata: {data['total']}")
    print(f"Page metadata: {data['page']}")
    
    if len(data['orders']) == 5:
        print("SUCCESS: Pagination limit works")
    else:
        print(f"FAILURE: Expected 5 orders, got {len(data['orders'])}")
        
    if data['total'] == count:
        print("SUCCESS: Total count matches DB")
    else:
        print(f"FAILURE: Total count mismatch. DB: {count}, API: {data['total']}")
else:
    print(f"Error: {data}")
