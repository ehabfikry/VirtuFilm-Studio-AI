import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('runpod_api_key')
q = """
query {
  __schema {
    mutationType {
      fields {
        name
        args {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
    }
  }
}
"""
r = requests.post('https://api.runpod.io/graphql', headers={'Authorization': f'Bearer {key}'}, json={'query': q})
data = r.json()
fields = data.get('data', {}).get('__schema', {}).get('mutationType', {}).get('fields', [])
deploy_field = [f for f in fields if 'deploy' in f['name'].lower()]
for df in deploy_field:
    print(df['name'], df['args'])
