with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[:56] + ['  <script src="https://cdn.tailwindcss.com"></script>\n\n'] + lines[99:]

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Replaced lines 56-99 with clean tailwind script!")
