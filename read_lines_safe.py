import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
with open('C:\\Users\\DELL\Desktop\\Cindy-AI-Director\\cindy_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2260, 2325):
    print(f'{i+1}: {lines[i]}', end='')
