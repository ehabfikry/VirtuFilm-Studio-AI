import math
import numpy as np
import torch
import torch.nn as nn

class CameraPoseEncoder(nn.Module):
    """
    Transforms 4x4 camera extrinsic matrices into Plücker coordinate ray embeddings
    or harmonic positional embeddings for cross-attention injection.
    """
    def __init__(self, embed_dim=768, num_freqs=8):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_freqs = num_freqs
        
        # 12-dimensional flattened extrinsic parameter [R (9) + T (3)]
        in_dim = 12 + 12 * 2 * num_freqs
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, embed_dim),
            nn.SiLU(),
            nn.Linear(embed_dim, embed_dim)
        )

    def _harmonic_encoding(self, x):
        freq_bands = 2.0 ** torch.linspace(0, self.num_freqs - 1, self.num_freqs, device=x.device)
        # x: [B, F, 12]
        x_expanded = x.unsqueeze(-1) * freq_bands # [B, F, 12, num_freqs]
        sin_enc = torch.sin(2.0 * math.pi * x_expanded).flatten(-2)
        cos_enc = torch.cos(2.0 * math.pi * x_expanded).flatten(-2)
        return torch.cat([x, sin_enc, cos_enc], dim=-1)

    def forward(self, extrinsics):
        """
        extrinsics: Tensor of shape [Batch, Frames, 4, 4] or numpy array
        returns: Camera embeddings of shape [Batch, Frames, embed_dim]
        """
        if isinstance(extrinsics, np.ndarray):
            extrinsics = torch.from_numpy(extrinsics)
        if extrinsics.dim() == 3:
            extrinsics = extrinsics.unsqueeze(0) # add batch dim
            
        device = next(self.parameters()).device if list(self.parameters()) else extrinsics.device
        extrinsics = extrinsics.to(device)

        # Flatten R (3x3) and T (3x1) -> 12 values
        rt = torch.cat([extrinsics[..., :3, :3].reshape(*extrinsics.shape[:2], 9), extrinsics[..., :3, 3]], dim=-1)
        encoded_rt = self._harmonic_encoding(rt)
        cam_embeds = self.mlp(encoded_rt)
        return cam_embeds
