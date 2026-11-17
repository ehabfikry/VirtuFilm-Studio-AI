import sys
import os

# Add Cindy-AI-Director root to path
sys.path.insert(0, r"C:\Users\DELL\Desktop\Cindy-AI-Director")

import torch
from cindy_engine.pipeline.cindy_generator import CindyVideoEngine

def test_engine_initialization():
    print("=" * 60)
    print("🧪 TESTING CINDY FOUNDATION VIDEO ENGINE")
    print("=" * 60)

    # 1. Initialize Engine
    engine = CindyVideoEngine(device="cpu")
    print(" Engine successfully created!")

    # 2. Test 3D Orbit Trajectory Generation & Camera Encoder
    num_frames = 24
    extrinsics, cam_embeds = engine.build_camera_conditioning(trajectory_type="orbit_360", num_frames=num_frames)
    print(f" Camera extrinsics shape: {extrinsics.shape} (Expected: ({num_frames}, 4, 4))")
    print(f" Camera embeddings shape: {cam_embeds.shape} (Expected: (1, {num_frames}, 768))")
    assert extrinsics.shape == (num_frames, 4, 4), "Extrinsics shape mismatch"
    assert cam_embeds.shape == (1, num_frames, 768), "Camera embeddings shape mismatch"

    # 3. Test 3D Gaussian Noise Prior
    latent_shape = (1, 4, num_frames, 64, 64)
    noise = engine.build_initial_noise(latent_shape=latent_shape, cov_alpha=0.05, seed=42)
    print(f" Initial noise shape: {noise.shape} (Expected: {latent_shape})")
    assert noise.shape == latent_shape, "Noise shape mismatch"

    # 4. Test Zero-Shot Identity Anchor
    test_latents = torch.randn(1, 320, num_frames, 32, 32)
    anchored = engine.identity_anchor(test_latents)
    print(f" Anchored latents shape: {anchored.shape} (Expected: {test_latents.shape})")
    assert anchored.shape == test_latents.shape, "Anchored latents shape mismatch"

    print("\n🎉 ALL CORE ENGINE MODULE TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_engine_initialization()
