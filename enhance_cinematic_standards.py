import os
import sys
import math
import cv2
import numpy as np

OUTPUTS_DIR = r"C:\Users\DELL\Desktop\Cindy-AI-Director\outputs"
CINEMATIC_DIR = os.path.join(OUTPUTS_DIR, "cinematic_standards")
os.makedirs(CINEMATIC_DIR, exist_ok=True)

def interpolate_frames_optical_flow(prev_frame, next_frame, alpha):
    """
    Bi-directional dense optical flow frame synthesis.
    alpha in (0, 1) represents the interpolation fraction.
    """
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    # Calculate forward and backward optical flows
    flow_forward = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    flow_backward = cv2.calcOpticalFlowFarneback(next_gray, prev_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    h, w = prev_gray.shape
    y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)

    # Warp forward from prev_frame
    map_x_prev = np.clip(x_coords + flow_forward[..., 0] * alpha, 0, w - 1).astype(np.float32)
    map_y_prev = np.clip(y_coords + flow_forward[..., 1] * alpha, 0, h - 1).astype(np.float32)
    warped_prev = cv2.remap(prev_frame, map_x_prev, map_y_prev, cv2.INTER_LINEAR)

    # Warp backward from next_frame
    map_x_next = np.clip(x_coords + flow_backward[..., 0] * (1.0 - alpha), 0, w - 1).astype(np.float32)
    map_y_next = np.clip(y_coords + flow_backward[..., 1] * (1.0 - alpha), 0, h - 1).astype(np.float32)
    warped_next = cv2.remap(next_frame, map_x_next, map_y_next, cv2.INTER_LINEAR)

    # Blend proportional to alpha
    blended = cv2.addWeighted(warped_prev, 1.0 - alpha, warped_next, alpha, 0)
    return blended

def process_cinematic_framing_and_upscale(frame, target_w=1280, target_h=720):
    """
    Cinematic framing: preserves subject aspect ratio, applies subtle pillar/letterboxing or
    smart border extension if needed, and applies Lanczos-4 high-fidelity spatial upscaling
    with a gentle unsharp mask to preserve fine facial and texture details without artifacts.
    """
    src_h, src_w = frame.shape[:2]
    src_aspect = src_w / src_h
    target_aspect = target_w / target_h

    if abs(src_aspect - target_aspect) < 0.05:
        # Aspect ratios match closely (e.g. 16:9)
        scaled = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    elif src_aspect < target_aspect:
        # Source is taller / square (e.g. 1:1 512x512) -> Fit height, center, and blend blurred background wings
        scaled_w = int(round(target_h * src_aspect))
        scaled_h = target_h
        resized_fg = cv2.resize(frame, (scaled_w, scaled_h), interpolation=cv2.INTER_LANCZOS4)

        # Blurred backdrop to give premium cinematic depth instead of harsh black borders
        bg_blurred = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        bg_blurred = cv2.GaussianBlur(bg_blurred, (51, 51), 30)
        bg_blurred = (bg_blurred * 0.4).astype(np.uint8)

        x_offset = (target_w - scaled_w) // 2
        bg_blurred[:, x_offset:x_offset + scaled_w] = resized_fg
        scaled = bg_blurred
    else:
        # Source is wider -> Fit width, letterbox with soft dark cinematic bars
        scaled_w = target_w
        scaled_h = int(round(target_w / src_aspect))
        resized_fg = cv2.resize(frame, (scaled_w, scaled_h), interpolation=cv2.INTER_LANCZOS4)

        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        y_offset = (target_h - scaled_h) // 2
        canvas[y_offset:y_offset + scaled_h, :] = resized_fg
        scaled = canvas

    # Detail-Preserving Unsharp Mask (high-frequency enhancement for skin & fabric textures)
    gaussian = cv2.GaussianBlur(scaled, (0, 0), 2.0)
    enhanced = cv2.addWeighted(scaled, 1.25, gaussian, -0.25, 0)
    return enhanced

def convert_video_to_cinematic_standard(src_path, dst_path, target_fps=24.0, target_w=1280, target_h=720):
    print(f"\n[CINEMATIC] Converting: {os.path.basename(src_path)} -> {target_w}x{target_h} @ {target_fps} fps...", flush=True)
    cap = cv2.VideoCapture(src_path)
    if not cap.isOpened():
        print(f" [ERROR] Could not open {src_path}", flush=True)
        return False

    src_fps = cap.get(cv2.CAP_PROP_FPS)
    src_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    src_duration = src_cnt / src_fps

    raw_frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        raw_frames.append(frame)
    cap.release()

    if len(raw_frames) == 0:
        print(f" [ERROR] No frames extracted from {src_path}", flush=True)
        return False

    total_target_frames = int(round(src_duration * target_fps))
    print(f" Source: {src_w}x{src_h} @ {src_fps:.1f} fps ({len(raw_frames)} frames, {src_duration:.2f}s)", flush=True)
    print(f" Target: {target_w}x{target_h} @ {target_fps:.1f} fps ({total_target_frames} frames)", flush=True)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_writer = cv2.VideoWriter(dst_path, fourcc, target_fps, (target_w, target_h))

    for target_idx in range(total_target_frames):
        target_time = target_idx / target_fps
        src_pos = target_time * src_fps
        src_base_idx = int(math.floor(src_pos))
        alpha = src_pos - src_base_idx

        if src_base_idx >= len(raw_frames) - 1:
            frame_interp = raw_frames[-1]
        elif alpha < 1e-4:
            frame_interp = raw_frames[src_base_idx]
        else:
            frame_interp = interpolate_frames_optical_flow(raw_frames[src_base_idx], raw_frames[src_base_idx + 1], alpha)

        frame_cinematic = process_cinematic_framing_and_upscale(frame_interp, target_w, target_h)
        out_writer.write(frame_cinematic)

    out_writer.release()
    print(f" [DONE] Saved cinematic video: {dst_path} ({os.path.getsize(dst_path):,} bytes)", flush=True)
    return True

def main():
    target_tools = [
        ("test_03_seine_transition.mp4", "cinema_01_seine_transition_24fps_hd.mp4", 1280, 720),
        ("test_02_dreamidv_bull_aziz.mp4", "cinema_02_dreamidv_bull_aziz_hd.mp4", 1280, 720),
        ("test_04_motioncanvas_drone.mp4", "cinema_03_motioncanvas_drone_24fps_hd.mp4", 1280, 720),
        ("test_05_motionpro_camera.mp4", "cinema_04_motionpro_camera_24fps_hd.mp4", 1280, 720),
        ("test_06_ttm_dualclock.mp4", "cinema_05_ttm_dualclock_24fps_hd.mp4", 1280, 720),
        ("test_07_mtvcrafter_4dmot.mp4", "cinema_06_mtvcrafter_4dmot_24fps_hd.mp4", 1280, 720),
        ("test_08_pisco_insertion.mp4", "cinema_07_pisco_insertion_24fps_hd.mp4", 1280, 720),
        ("test_09_magicme_idlock.mp4", "cinema_08_magicme_idlock_24fps_hd.mp4", 1280, 720)
    ]

    for src_name, dst_name, tw, th in target_tools:
        src_path = os.path.join(OUTPUTS_DIR, src_name)
        dst_path = os.path.join(CINEMATIC_DIR, dst_name)
        if os.path.exists(src_path):
            convert_video_to_cinematic_standard(src_path, dst_path, target_fps=24.0, target_w=tw, target_h=th)
        else:
            print(f"[SKIP] Source file not found: {src_path}", flush=True)

if __name__ == "__main__":
    main()
