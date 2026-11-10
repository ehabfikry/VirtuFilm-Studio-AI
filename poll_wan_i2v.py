import requests, json, time, os

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('fal_api_key')
headers = {'Authorization': f'Key {key}'}

status_url = "https://queue.fal.run/fal-ai/wan-i2v/requests/01a1a606-143e-7261-93e3-5868a946a0db/status"
response_url = "https://queue.fal.run/fal-ai/wan-i2v/requests/01a1a606-143e-7261-93e3-5868a946a0db"

start = time.time()
while time.time() - start < 180:
    time.sleep(5)
    r = requests.get(status_url, headers=headers, timeout=15)
    data = r.json()
    status = data.get('status')
    elapsed = int(time.time() - start)
    print(f"[{elapsed}s] Status: {status}")
    if status == 'COMPLETED':
        res = requests.get(response_url, headers=headers, timeout=20)
        res_data = res.json()
        print("Response data:", json.dumps(res_data, indent=2)[:500])
        vid_obj = res_data.get('video')
        vid_url = vid_obj.get('url') if isinstance(vid_obj, dict) else res_data.get('video_url')
        if vid_url:
            out_name = f"Wan21_Tube_Map_{int(time.time())}.mp4"
            out_path = os.path.join(r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs', out_name)
            content = requests.get(vid_url, timeout=40).content
            with open(out_path, 'wb') as vf:
                vf.write(content)
            print(f"SUCCESS! Downloaded {len(content)} bytes to {out_path}")
        break
    elif status in ['FAILED', 'ERROR']:
        print("Failed:", data)
        break
