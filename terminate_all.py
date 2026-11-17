import json, requests

sec = json.load(open(r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"))
key = sec.get("runpod_api_key")
headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}

# Terminate all active pods to be 100% clean
r = requests.post("https://api.runpod.io/graphql", headers=headers, json={"query": "query { myself { pods { id name } } }"})
pods = r.json().get("data", {}).get("myself", {}).get("pods", [])
print("Active pods before terminate:", pods)

for p in pods:
    pid = p["id"]
    r_term = requests.post("https://api.runpod.io/graphql", headers=headers, json={"query": 'mutation { podTerminate(input: {podId: "%s"}) }' % pid})
    print(f"Terminated pod {pid}:", r_term.json())

# Verify
r_after = requests.post("https://api.runpod.io/graphql", headers=headers, json={"query": "query { myself { pods { id } } }"})
print("Active pods after terminate:", r_after.json().get("data", {}).get("myself", {}).get("pods", []))
