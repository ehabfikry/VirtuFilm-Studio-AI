import requests, json, time, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

from cindy_server import upload_file_to_fal, OUTPUTS_DIR

fal_key = secrets.get('fal_api_key', '').strip()
local_img_path = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\upload_1793783555303_Man_reading_Tube_map_6f8b4f7f.jpg'

print("Uploading to Fal...")
cloud_img = upload_file_to_fal(local_img_path, fal_key)
print("cloud_img:", cloud_img)

p_text = "The young man is lost in reading the subway map, scratching his head, looking arround, locked camera"
fal_payload = {"prompt": p_text, "image_url": cloud_img}
sub_r = requests.post("https://queue.fal.run/fal-ai/wan-i2v", headers={'Authorization': f'Key {fal_key}', 'Content-Type': 'application/json'}, json=fal_payload, timeout=25)
print("Sub status:", sub_r.status_code, sub_r.text[:200])
