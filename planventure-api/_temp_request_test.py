import json
import urllib.request

url = 'http://127.0.0.1:5000/auth/register'
data = json.dumps({'email': 'test2@example.com', 'password': 'Password123'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=10)
print(resp.status)
print(resp.read().decode())
