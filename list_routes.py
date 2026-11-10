import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

routes = re.findall(r'self\.path\s*==\s*[\'"]([^\'"]+)[\'"]|self\.path\.startswith\([\'"]([^\'"]+)[\'"]\)', text)
print('Routes in cindy_server.py:')
for r in routes:
    print(' ', r[0] or r[1])
