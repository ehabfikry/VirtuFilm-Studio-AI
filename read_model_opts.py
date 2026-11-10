import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="active-video-model"')
end_idx = text.find('</select>', idx)
print(text[idx:end_idx+9])
