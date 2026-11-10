import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('runpod_api_key')
RUNPOD_GQL = f'https://api.runpod.io/graphql?api_key={key}'

q = """
mutation {
  podFindAndDeployOnDemand(input: {
    name: "test"
    templateId: "cw3nka7d08"
    gpuTypeId: "NVIDIA GeForce RTX 4090"
    dockerArgs: "bash -c 'echo hello'"
    env: [{key: "TEST", value: "1"}]
    dryRunTest2: 123
  }) {
    id
  }
}
"""
r = requests.post(RUNPOD_GQL, json={'query': q})
errs = r.json().get('errors', [])
print("Errors:")
for e in errs:
    print(e.get('message'))
