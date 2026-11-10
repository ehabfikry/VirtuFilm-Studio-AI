import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

funcs = re.findall(r'def\s+([a-zA-Z0-9_]*video[a-zA-Z0-9_]*)\(', text)
print('Video handlers in cindy_server.py:', funcs)

funcs_gen = re.findall(r'def\s+(handle_[a-zA-Z0-9_]*)\(', text)
print('All handlers:', funcs_gen)
