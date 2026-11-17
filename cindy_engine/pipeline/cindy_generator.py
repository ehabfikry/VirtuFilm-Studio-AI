import os
import sys
import torch
import numpy as np
from cindy_engine.camera.trajectories import CameraTrajectory
from cindy_engine.camera.camera_encoder import CameraPoseEncoder
from cindy_engine.identity.zero_shot_anchor import ZeroShotIdentityAnchor
from cindy_engine.identity.gaussian_prior import GaussianNoisePrior
from cindy_engine.postprocess.cinema_standards import CinemaPostProcessor

class CindyVideoEngine:
    """
    Cindy AI Director - Foundation Video Generation Engine.
    Coordinates explicit 3D camera trajectory guidance, zero-shot identity persistence,
    and automated cinema standardization into a unified generation interface.
    """
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        print(f"[CindyEngine] Initializing Cindy Foundation Video Engine on device: {self.device}")
        
        self.camera_encoder = CameraPoseEncoder(embed_dim=768).to(self.device)
        self.identity_anchor = ZeroShotIdentityAnchor(channels=320).to(self.device)
        self.postprocessor = CinemaPostProcessor(target_width=1280, target_height=720, target_fps=24.0)
        print("[CindyEngine] Core sub-modules loaded successfully.")

    def build_camera_conditioning(self, trajectory_type="orbit_360", num_frames=24, **kwargs):
        """
        Computes 3D camera extrinsics and projects into harmonic camera embeddings.
        """
        print(f"[CindyEngine] Computing camera trajectory: '{trajectory_type}' across {num_frames} frames...")
        extrinsics = CameraTrajectory.get_trajectory(mode=trajectory_type, num_frames=num_frames, **kwargs)
        cam_embeds = self.camera_encoder(extrinsics)
        return extrinsics, cam_embeds

    def build_initial_noise(self, latent_shape, cov_alpha=0.05, seed=None):
        """
        Generates 3D Gaussian Noise Prior with Toeplitz temporal covariance.
        """
        generator = torch.Generator(device=self.device)
        if seed is not None:
            generator.manual_seed(seed)
        noise = GaussianNoisePrior.generate_correlated_noise(
            shape=latent_shape,
            cov_alpha=cov_alpha,
            generator=generator,
            device=self.device
        )
        return noise

    def enhance_to_cinema(self, raw_video_path, output_hd_path):
        """
        Post-processes raw output to 1280x720 @ 24fps HD.
        """
        print(f"[CindyEngine] Post-processing to cinema standard: {output_hd_path}...")
        return self.postprocessor.process_video(raw_video_path, output_hd_path)
