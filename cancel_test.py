import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('fal_api_key')
headers = {'Authorization': f'Key {key}'}

r1 = requests.put("https://queue.fal.run/fal-ai/wan/requests/01a1a5fe-4b17-7180-b42d-46c8901e56e0/cancel", headers=headers)
r2 = requests.put("https://queue.fal.run/fal-ai/wan/requests/01a1a5fe-4da2-7462-9fdd-77a5329fb264/cancel", headers=headers)
r3 = requests.put("https://queue.fal.run/fal-ai/wan-t2v/requests/01a1a5fe-5029-7ef0-8437-d6e62935240a/cancel", headers=headers)
print("Cancelled:", r1.status_code, r2.status_code, r3.status_code)
