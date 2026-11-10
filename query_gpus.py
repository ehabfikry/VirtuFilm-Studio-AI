import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
s = json.load(open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json', encoding='utf-8'))
key = s.get('runpod_api_key')
RUNPOD_GQL = f'https://api.runpod.io/graphql?api_key={key.strip()}'
q = """
query {
  gpuTypes {
    id
    displayName
    memoryInGb
    communityPrice
    lowestPrice(input: {gpuCount: 1}) {
      minimumBidPrice
      uninterruptablePrice
    }
  }
}
"""
r = requests.post(RUNPOD_GQL, json={"query": q})
data = r.json()
gpus = data.get("data", {}).get("gpuTypes", [])
# Filter for GPUs with >= 16 GB VRAM suitable for ComfyUI / Video
viable = []
for g in gpus:
    mem = g.get("memoryInGb", 0)
    lp = g.get("lowestPrice") or {}
    price = lp.get("uninterruptablePrice") or g.get("communityPrice") or 999
    if mem >= 16 and price > 0:
        viable.append({
            "id": g["id"],
            "name": g["displayName"],
            "vram": mem,
            "price": price
        })

# Sort ascending by price!
viable.sort(key=lambda x: x["price"])

print(f"Total viable GPUs (>=16GB VRAM): {len(viable)}")
for v in viable[:15]:
    print(f"{v['name']:35} | {v['vram']:2}GB VRAM | ${v['price']:.2f}/hr | ID: {v['id']}")
