with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect handle_comfyui_generate_video
target = '''        # Resolve local path for image
        if image_url.startswith('data:'):
            try:
                header, b64data = image_url.split(';base64,', 1)
                raw = base64.b64decode(b64data)
                mtype, ext = _detect_magic_media(raw, 'reference.png')
                fname = f"ref_{int(time.time() * 1000)}.{ext or 'png'}"
                local_img_path = os.path.join(OUTPUTS_DIR, fname)
                with open(local_img_path, 'wb') as fh:
                    fh.write(raw)
            except Exception as e:
                self.send_error_response(400, f"فشل قراءة كادر الصورة المرجعية: {e}")
                return
        else:
            clean_img = image_url.split('?')[0]
            if clean_img.startswith('/outputs/'):
                local_img_path = os.path.join(OUTPUTS_DIR, os.path.basename(clean_img))
            elif os.path.isabs(clean_img):
                local_img_path = clean_img
            else:
                local_img_path = os.path.join(OUTPUTS_DIR, os.path.basename(clean_img))

            if not os.path.exists(local_img_path):
                self.send_error_response(404, f"ملف الصورة غير موجود: {image_url}")
                return



        # Upload image to ComfyUI input directory
        uploaded_name = None
        try:
            uploaded_name = comfyui_client.upload_image_to_comfyui(url, local_img_path)
        except Exception as e:
            err_up = str(e)
            fal_key = secrets.get('fal_api_key', '').strip()
            if ('wan' in ckpt_lower) and fal_key:'''

replacement = '''        # Extract video parameters early so they are available in fallback
        ckpt = payload.get('checkpoint', 'SVD/svd_xt.safetensors')
        ckpt_lower = str(ckpt).lower()
        width = int(payload.get('width', 1024))
        height = int(payload.get('height', 576))
        video_frames = int(payload.get('video_frames', 25))
        motion_bucket_id = int(payload.get('motion_bucket_id', 127))
        fps = int(payload.get('fps', 6))
        steps = int(payload.get('steps', 20))
        auto_stop = bool(payload.get('auto_stop', True))

        # Resolve local path for image
        if image_url.startswith('data:'):
            try:
                header, b64data = image_url.split(';base64,', 1)
                raw = base64.b64decode(b64data)
                mtype, ext = _detect_magic_media(raw, 'reference.png')
                fname = f"ref_{int(time.time() * 1000)}.{ext or 'png'}"
                local_img_path = os.path.join(OUTPUTS_DIR, fname)
                with open(local_img_path, 'wb') as fh:
                    fh.write(raw)
            except Exception as e:
                self.send_error_response(400, f"فشل قراءة كادر الصورة المرجعية: {e}")
                return
        else:
            clean_img = image_url.split('?')[0]
            if clean_img.startswith('/outputs/'):
                local_img_path = os.path.join(OUTPUTS_DIR, os.path.basename(clean_img))
            elif os.path.isabs(clean_img):
                local_img_path = clean_img
            else:
                local_img_path = os.path.join(OUTPUTS_DIR, os.path.basename(clean_img))

            if not os.path.exists(local_img_path):
                self.send_error_response(404, f"ملف الصورة غير موجود: {image_url}")
                return

        # Upload image to ComfyUI input directory
        uploaded_name = None
        try:
            uploaded_name = comfyui_client.upload_image_to_comfyui(url, local_img_path)
        except Exception as e:
            err_up = str(e)
            fal_key = secrets.get('fal_api_key', '').strip()
            if ('wan' in ckpt_lower) and fal_key:'''

if target in text:
    text = text.replace(target, replacement, 1)
    print("Fixed ckpt_lower definition order!")
else:
    print("Target not found verbatim")

with open(r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved cindy_server.py!")
