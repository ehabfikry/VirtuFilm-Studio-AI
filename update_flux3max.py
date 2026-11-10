with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = "elif 'veo3' in ep:"
replacement = """elif 'flux-3-max' in ep:
                applied = min([5, 10, 15, 20], key=lambda x: abs(x - dur))
                req_body.update({
                    'duration': applied,
                    'aspect_ratio': ar,
                    'generate_audio': True,
                    'reasoning_level': 'high'
                })
            elif 'veo3' in ep:"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated cindy_server.py with flux-3-max parameters")
else:
    print("ERROR: Target not found")
