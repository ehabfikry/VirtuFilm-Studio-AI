import os, shutil

# 1. Purge generate_enhanced_html.py
p = r'C:\Users\DELL\Desktop\Cindy-AI-Director\generate_enhanced_html.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace all occurrences
text = text.replace("<!-- When in Serverless Mode (LivePortrait / LatentSync) -->", "<!-- When in Dedicated Mode (Kling Motion Control / LatentSync) -->")
text = text.replace("comfy-mimic-source-img", "comfy-kling-actor-img")
text = text.replace("comfy-mimic-char-preview", "comfy-kling-actor-preview")
text = text.replace("comfy-mimic-char-placeholder", "comfy-kling-actor-placeholder")
text = text.replace("comfy-mimic-char-badge", "comfy-kling-actor-badge")

text = text.replace("comfy-mimic-driving-video", "comfy-kling-driving-vid")
text = text.replace("comfy-mimic-video-preview", "comfy-kling-video-preview")
text = text.replace("comfy-mimic-video-placeholder", "comfy-kling-video-placeholder")
text = text.replace("comfy-mimic-video-badge", "comfy-kling-video-badge")

text = text.replace("MimicMotion_Kling_Render.mp4", "Kling_Motion_Render.mp4")
text = text.replace("uploadLivePortraitVideo", "uploadKlingMotionVideo")
text = text.replace("useLastRenderedImageForLivePortrait", "useLastRenderedImageForKlingMotion")
text = text.replace("تم تعيين آخر كادر لصالح LivePortrait!", "تم تعيين آخر كادر لصالح Kling Motion Control!")
text = text.replace("currentComfySubMode === 'liveportrait'", "currentComfySubMode === 'kling'")
text = text.replace("'/api/comfyui/liveportrait'", "'/api/comfyui/motion_control'")
text = text.replace("`/api/comfyui/liveportrait`", "`/api/comfyui/motion_control`")

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)

# Also copy render file if exists
src_vid = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\MimicMotion_Kling_Render.mp4'
dst_vid = r'C:\Users\DELL\Desktop\Cindy-AI-Director\outputs\Kling_Motion_Render.mp4'
if os.path.exists(src_vid) and not os.path.exists(dst_vid):
    shutil.copyfile(src_vid, dst_vid)
    print("Copied video render to Kling_Motion_Render.mp4")

print("generate_enhanced_html.py purged completely.")
