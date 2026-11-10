import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'def handle_comfyui_generate_video' in l:
        for j in range(i, min(i+110, len(lines))):
            print(f"{j+1}: {lines[j]}", end="")
        break
