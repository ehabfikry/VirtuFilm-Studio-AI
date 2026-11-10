import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('endpoint_mapping = {')
if idx != -1:
    end_idx = text.find('}', idx)
    print(text[idx:end_idx+1])
