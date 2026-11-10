import requests, json

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)
key = s.get('runpod_api_key')
RUNPOD_GQL = f'https://api.runpod.io/graphql?api_key={key}'

templates_to_check = ['758dsjwiqz', 'ipbtjo67kk', 'cw3nka7d08', '0dh8mbtpld', 'ljqzbo5bw9']

for tid in templates_to_check:
    q = """
    query {
      podTemplate(id: "%s") {
        id
        name
        imageName
        dockerArgs
        containerDiskInGb
        volumeInGb
        volumeMountPath
        ports
        env {
          key
          value
        }
      }
    }
    """ % tid
    r = requests.post(RUNPOD_GQL, json={'query': q})
    tmpl = r.json().get('data', {}).get('podTemplate')
    print(f"=== Template: {tid} ===")
    if tmpl:
        print(f"Name: {tmpl.get('name')}")
        print(f"Image: {tmpl.get('imageName')}")
        print(f"DockerArgs: {tmpl.get('dockerArgs')}")
        print(f"Ports: {tmpl.get('ports')}")
        print(f"Env: {tmpl.get('env')}")
    else:
        print("Not found or error:", r.json().get('errors'))
