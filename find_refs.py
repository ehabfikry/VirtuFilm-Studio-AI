import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Search for reference input elements
refs = re.findall(r'id=["\']([^"\']*(?:ref|upload|source|driving|character|input)[^"\']*)["\']', text, re.IGNORECASE)
print('Unique input/ref IDs found:')
for r in sorted(set(refs)):
    if any(k in r.lower() for k in ['ref', 'media', 'img', 'video', 'file', 'source', 'char']):
        print(f"  - {r}")
