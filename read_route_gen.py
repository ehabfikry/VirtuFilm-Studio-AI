import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find("self.path == '/api/generate'")
if idx != -1:
    print(text[idx-50:idx+400])
