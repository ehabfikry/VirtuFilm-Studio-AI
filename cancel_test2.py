import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('fal_api_key')
headers = {'Authorization': f'Key {key}'}

r1 = requests.put("https://queue.fal.run/fal-ai/wan-i2v/requests/01a1a605-6b1d-70b3-8171-d5f6bb69ce07/cancel", headers=headers)
print("Cancel:", r1.status_code)
