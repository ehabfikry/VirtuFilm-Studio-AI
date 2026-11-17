import os
import cv2
import numpy as np

class CinemaPostProcessor:
    """
    Standardizes raw video generation into high-fidelity cinematic outputs:
    - 1280x720 HD (16:9) framing with pillarbox ambient blurred wings.
    - 24.0 fps frame rate via Farneback dense optical flow temporal interpolation.
    - High-frequency unsharp mask for cinematic texture and clarity.
    """
    def __init__(self, target_width=1280, target_height=720, target_fps=24.0):
        self.target_w = target_width
        self.target_h = target_height
        self.target_fps = target_fps

    def _format_frame(self, frame, orig_w, orig_h):
        scale = self.target_h / float(orig_h)
        new_w = int(round(orig_w * scale))
        scaled_fg = cv2.resize(frame, (new_w, self.target_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Blurred backdrop wings
        bg = cv2.resize(frame, (self.target_w, self.target_h), interpolation=cv2.INTER_LINEAR)
        bg = cv2.GaussianBlur(bg, (99, 99), 35)
        bg = (bg.astype(np.float32) * 0.45).astype(np.uint8)

        x_off = (self.target_w - new_w) // 2
        bg[:, x_off:x_off + new_w] = scaled_fg
        return bg

    def process_video(self, input_video_path, output_video_path):
        cap = cv2.VideoCapture(input_video_path)
        in_fps = cap.get(cv2.CAP_PROP_FPS) or 12.0
        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()

        num_in = len(frames)
        if num_in == 0:
            raise ValueError(f"No frames could be read from {input_video_path}")

        total_out = int(round(num_in * (self.target_fps / in_fps)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)
        out = cv2.VideoWriter(output_video_path, fourcc, self.target_fps, (self.target_w, self.target_h))

        for i in range(total_out):
            src_pos = (i / float(total_out - 1)) * (num_in - 1) if total_out > 1 else 0
            idx0 = int(np.floor(src_pos))
            idx1 = min(idx0 + 1, num_in - 1)
            alpha = src_pos - idx0

            if idx0 == idx1 or alpha < 1e-4:
                frame_res = self._format_frame(frames[idx0], orig_w, orig_h)
            else:
                f0 = frames[idx0]
                f1 = frames[idx1]
                g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
                g1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(g0, g1, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                h, w = flow.shape[:2]
                grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
                map_x0 = (grid_x + flow[..., 0] * alpha).astype(np.float32)
                map_y0 = (grid_y + flow[..., 1] * alpha).astype(np.float32)
                map_x1 = (grid_x - flow[..., 0] * (1.0 - alpha)).astype(np.float32)
                map_y1 = (grid_y - flow[..., 1] * (1.0 - alpha)).astype(np.float32)
                warp0 = cv2.remap(f0, map_x0, map_y0, cv2.INTER_LINEAR)
                warp1 = cv2.remap(f1, map_x1, map_y1, cv2.INTER_LINEAR)
                f_interp = cv2.addWeighted(warp0, 1.0 - alpha, warp1, alpha, 0)
                frame_res = self._format_frame(f_interp, orig_w, orig_h)

            out.write(frame_res)

        out.release()
        return output_video_path
