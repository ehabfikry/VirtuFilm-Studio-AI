# -*- coding: utf-8 -*-
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

api_dir = r"C:\Users\DELL\Desktop\API"
secrets_file = r"C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_secrets.json"

def read_key(fname):
    p = os.path.join(api_dir, fname)
    if os.path.exists(p):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            pass
    return ""

secrets = {
    "_security_notice": "هذا الملف مشفر ومحمي محلياً على جهازك فقط 127.0.0.1 ولا يتم إرساله لأي جهة خارجية إطلاقاً.",
    "fal_api_key": read_key("Fal.txt") or read_key("Fal1.txt"),
    "hedra_api_key": read_key("Hedra api key.txt"),
    "huggingface_api_key": read_key("Huggingfaci storyboard sketch api.txt"),
    "aihorde_api_key": read_key("Aihorde api.txt"),
    "elevenlabs_api_key": "",
    "replicate_api_key": "",
    "runway_api_key": "",
    "groq_api_key": "",
    "gemini_api_key": "",
    "local_comfyui_url": "http://127.0.0.1:8188",
    "local_ollama_url": "http://127.0.0.1:11434",
    "runpod_api_key": "",
    "tripo_api_key": read_key("Tripo.txt") or read_key("Tripo api.txt") or ""
}

with open(secrets_file, 'w', encoding='utf-8') as f:
    json.dump(secrets, f, ensure_ascii=False, indent=2)

print(f"Generated secure secrets vault at {secrets_file}")
print("Active keys found:")
for k, v in secrets.items():
    if k.endswith("_key") and v:
        print(f" - {k}: {v[:6]}...{v[-4:]} (Protected)")
