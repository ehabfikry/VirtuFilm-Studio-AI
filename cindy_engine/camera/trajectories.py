import math
import numpy as np
import torch

class CameraTrajectory:
    """
    Mathematical 3D Camera Trajectory Generator.
    Computes camera extrinsic matrices [R | T] and ray embeddings across discrete frames.
    """
    
    @staticmethod
    def orbit_360(num_frames=24, radius=2.5, height=0.2, center=(0.0, 0.0, 0.0), fov_deg=60.0):
        """
        Generates a continuous 360-degree horizontal circular orbit around a target point.
        """
        extrinsics = []
        for t in range(num_frames):
            theta = 2.0 * math.pi * (t / float(num_frames))
            cam_x = center[0] + radius * math.sin(theta)
            cam_z = center[2] + radius * math.cos(theta)
            cam_y = center[1] + height

            pos = np.array([cam_x, cam_y, cam_z], dtype=np.float32)
            target = np.array(center, dtype=np.float32)
            up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

            # LookAt matrix computation
            forward = target - pos
            forward = forward / (np.linalg.norm(forward) + 1e-8)
            right = np.cross(forward, up)
            right = right / (np.linalg.norm(right) + 1e-8)
            real_up = np.cross(right, forward)

            # Rotation matrix (World to Camera)
            R = np.vstack([right, -real_up, forward])
            T = -np.dot(R, pos)

            extrinsic = np.eye(4, dtype=np.float32)
            extrinsic[:3, :3] = R
            extrinsic[:3, 3] = T
            extrinsics.append(extrinsic)

        return np.stack(extrinsics, axis=0)

    @staticmethod
    def pan_horizontal(num_frames=24, start_x=-1.5, end_x=1.5, height=0.0, depth=2.5):
        """
        Generates a smooth horizontal pan camera movement.
        """
        extrinsics = []
        for t in range(num_frames):
            alpha = t / float(num_frames - 1) if num_frames > 1 else 0.0
            x = (1.0 - alpha) * start_x + alpha * end_x
            extrinsic = np.eye(4, dtype=np.float32)
            extrinsic[0, 3] = -x
            extrinsic[1, 3] = -height
            extrinsic[2, 3] = depth
            extrinsics.append(extrinsic)
        return np.stack(extrinsics, axis=0)

    @staticmethod
    def dolly_zoom(num_frames=24, start_dist=3.5, end_dist=1.5):
        """
        Generates forward or backward dolly zoom (Push-in / Pull-out).
        """
        extrinsics = []
        for t in range(num_frames):
            alpha = t / float(num_frames - 1) if num_frames > 1 else 0.0
            dist = (1.0 - alpha) * start_dist + alpha * end_dist
            extrinsic = np.eye(4, dtype=np.float32)
            extrinsic[2, 3] = dist
            extrinsics.append(extrinsic)
        return np.stack(extrinsics, axis=0)

    @classmethod
    def get_trajectory(cls, mode="orbit_360", num_frames=24, **kwargs):
        if mode == "orbit_360":
            return cls.orbit_360(num_frames=num_frames, **kwargs)
        elif mode == "pan_horizontal":
            return cls.pan_horizontal(num_frames=num_frames, **kwargs)
        elif mode == "dolly":
            return cls.dolly_zoom(num_frames=num_frames, **kwargs)
        else:
            # Static camera default
            return np.tile(np.eye(4, dtype=np.float32)[np.newaxis, ...], (num_frames, 1, 1))
