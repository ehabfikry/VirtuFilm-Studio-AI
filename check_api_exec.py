import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('/api/execute')
print(text[idx-100:idx+300])
