import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'r', encoding='utf-8') as f:
    text = f.read()

funcs = re.findall(r'function\s+([a-zA-Z0-9_]*send[a-zA-Z0-9_]*|[a-zA-Z0-9_]*generate[a-zA-Z0-9_]*|[a-zA-Z0-9_]*execute[a-zA-Z0-9_]*)\(', text, re.IGNORECASE)
print('Execution functions:', funcs)
