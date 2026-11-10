import sys
sys.path.append(r'C:\Users\DELL\Desktop\Cindy-AI-Director')
import requests, json
from cindy_server import load_secrets, update_comfy_activity

key = load_secrets().get('runpod_api_key', '')
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
update_comfy_activity()

q = '''mutation {
  podResume(input: { podId: "nu11cs90y2pf2n", gpuCount: 1 }) {
    id
    desiredStatus
  }
}'''
r = requests.post('https://api.runpod.io/graphql', headers=headers, json={'query': q}, timeout=10)
print('Resume result:', json.dumps(r.json(), indent=2))
