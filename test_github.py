import requests, base64, os, json

token = os.environ.get('GITHUB_TOKEN', 'ghp_64...bJ3n')
headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

# Test fetch
r = requests.get('https://api.github.com/repos/newmanrueda/mundial2026/contents/data.json', headers=headers, timeout=10)
print('GET status:', r.status_code)
if r.status_code == 200:
    print('SHA:', r.json().get('sha','?')[:16])
else:
    print('Response:', r.text[:200])

# Test create/update with a simple test content
import datetime
test_content = json.dumps({"test": True, "time": str(datetime.datetime.now())})
b64 = base64.b64encode(test_content.encode()).decode()
payload = {"message": "test sync", "content": b64}

r2 = requests.put('https://api.github.com/repos/newmanrueda/mundial2026/contents/test_sync.json', headers=headers, json=payload, timeout=10)
print('\nPUT status:', r2.status_code)
if r2.status_code in (200, 201):
    print('Test file created!')
    # Now delete the test file
    sha = r2.json().get('content', {}).get('sha', r2.json().get('sha',''))
    r3 = requests.delete('https://api.github.com/repos/newmanrueda/mundial2026/contents/test_sync.json', 
                         headers=headers, json={"message": "cleanup test", "sha": sha}, timeout=10)
    print('Cleanup status:', r3.status_code)
else:
    print('Response:', r2.text[:300])
