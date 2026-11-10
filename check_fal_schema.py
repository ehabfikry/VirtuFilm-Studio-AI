import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('fal_api_key')
headers = {'Authorization': f'Key {key}'}

# OpenAPI schema endpoint for fal-ai/wan/v2.1/image-to-video
r = requests.get('https://api.fal.ai/v1/models/fal-ai/wan/v2.1/image-to-video/schema', headers=headers)
if r.status_code == 200:
    schema = r.json()
    props = schema.get('paths', {}).get('/', {}).get('post', {}).get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {}).get('properties', {})
    print("Wan 2.1 I2V Request properties:", list(props.keys()))
else:
    print("Schema status:", r.status_code, r.text)
