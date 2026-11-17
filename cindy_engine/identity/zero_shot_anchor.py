import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class ZeroShotIdentityAnchor(nn.Module):
    """
    Zero-Shot Identity Persistence Module.
    Extracts deep identity latent representations from the synthesized or user-conditioned
    first frame (F_0) and enforces temporal identity anchoring across the sequence F_1..F_N.
    """
    def __init__(self, channels=320):
        super().__init__()
        self.channels = channels
        self.proj_q = nn.Conv2d(channels, channels, 1)
        self.proj_k = nn.Conv2d(channels, channels, 1)
        self.proj_v = nn.Conv2d(channels, channels, 1)
        self.gamma = nn.Parameter(torch.zeros(1))

    def forward(self, hidden_states):
        """
        hidden_states: 5D Tensor [B, C, F, H, W]
        Returns identity-anchored hidden_states where F_0 acts as the permanent anchor.
        """
        B, C, F_len, H, W = hidden_states.shape
        if F_len <= 1:
            return hidden_states

        # Extract anchor frame (F_0)
        f0 = hidden_states[:, :, 0, :, :] # [B, C, H, W]
        k_anchor = self.proj_k(f0).reshape(B, C, H * W).permute(0, 2, 1) # [B, HW, C]
        v_anchor = self.proj_v(f0).reshape(B, C, H * W).permute(0, 2, 1) # [B, HW, C]

        out_frames = [hidden_states[:, :, 0:1, :, :]]

        # Anchor subsequent frames F_1..F_N against F_0
        scale = 1.0 / math.sqrt(C)
        for t in range(1, F_len):
            ft = hidden_states[:, :, t, :, :] # [B, C, H, W]
            q_t = self.proj_q(ft).reshape(B, C, H * W).permute(0, 2, 1) # [B, HW, C]

            # Attention scores: Q_t * K_anchor^T
            attn = torch.bmm(q_t, k_anchor.permute(0, 2, 1)) * scale
            attn = F.softmax(attn, dim=-1)

            # Reconstructed identity representation
            id_rep = torch.bmm(attn, v_anchor).permute(0, 2, 1).reshape(B, C, H, W)

            # Residual injection scaled by learned gamma
            ft_anchored = ft + self.gamma * id_rep
            out_frames.append(ft_anchored.unsqueeze(2))

        return torch.cat(out_frames, dim=2)
