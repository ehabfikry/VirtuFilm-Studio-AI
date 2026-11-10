import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'r', encoding='utf-8') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'active-video-model', text)]
print(f"Occurrences of active-video-model: {len(matches)}")
for idx in matches:
    print("---")
    print(text[max(0, idx-100):min(len(text), idx+200)])
