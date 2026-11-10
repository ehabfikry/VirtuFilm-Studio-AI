import json

transcript_path = r'C:\Users\DELL\.gemini\antigravity\brain\f39b14fe-7077-4fe2-88bb-d661dd89b5b3\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            obj = json.loads(line)
            if obj.get('step_index') == 7979:
                print(obj.get('tool_calls', [{}])[0].get('args', {}).get('CommandLine'))
                break
        except Exception:
            pass
