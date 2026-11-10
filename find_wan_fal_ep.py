import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
fal_key = s.get('fal_api_key')
headers = {'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}

img_url = "https://v3b.fal.media/files/b/0ab119e9/_tH9zINr4AuG-9hrH-u_9_upload_1793783555303_Man_reading_Tube_map_6f8b4f7f.jpg"
prompt = "The young man is lost in reading the subway map, scratching his head, looking around"

test_endpoints = [
    "fal-ai/wan/i2v",
    "fal-ai/wan-2.1/image-to-video",
    "fal-ai/wan2.1/image-to-video",
    "fal-ai/wan2.1-i2v",
    "fal-ai/wan/t2v",
    "fal-ai/wan-t2v",
    "fal-ai/wan21-i2v"
]

for ep in test_endpoints:
    submit_url = f"https://queue.fal.run/{ep}"
    payload = {"prompt": prompt, "image_url": img_url}
    r = requests.post(submit_url, headers=headers, json=payload, timeout=15)
    print(f"Endpoint: {ep} -> Status: {r.status_code}")
    if r.status_code in [200, 201, 202]:
        resp_url = r.json().get('response_url')
        status_url = r.json().get('status_url')
        print(f"  status_url: {status_url}")
        # Check immediately
        st = requests.get(status_url, headers=headers, timeout=10).json()
        print(f"  immediate status: {st.get('status')}")
