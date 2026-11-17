import torch
from torch.distributions.multivariate_normal import MultivariateNormal

class GaussianNoisePrior:
    """
    3D Gaussian Noise Covariance Generator (from Magic-Me / Dual-Clock principles).
    Provides structured temporal covariance (cov_alpha) to the initial latent noise
    distribution, preventing random facial drift during high-frequency diffusion denoising.
    """
    @staticmethod
    def generate_correlated_noise(shape, cov_alpha=0.05, generator=None, device="cpu", dtype=torch.float32):
        """
        shape: (batch_size, channels, num_frames, height, width)
        cov_alpha: Degree of inter-frame covariance correlation [0.0 = white noise, 0.1 = strongly correlated]
        """
        B, C, F, H, W = shape
        
        # Build Toeplitz temporal covariance matrix: K_{i,j} = (1 - alpha) * delta_{i,j} + alpha * exp(-|i - j| / tau)
        cov_matrix = torch.eye(F, device=device, dtype=dtype)
        for i in range(F):
            for j in range(F):
                if i != j:
                    cov_matrix[i, j] = cov_alpha * torch.exp(-torch.tensor(abs(i - j) / 2.0, device=device, dtype=dtype))
                else:
                    cov_matrix[i, j] = 1.0

        # Ensure positive-definiteness via Cholesky decomposition
        L = torch.linalg.cholesky(cov_matrix) # [F, F]

        # Draw standard Gaussian white noise
        white_noise = torch.randn((B, C, H, W, F), generator=generator, device=device, dtype=dtype)

        # Correlate across temporal axis: correlated = white_noise @ L^T
        correlated_noise = torch.matmul(white_noise, L.T) # [B, C, H, W, F]

        # Permute back to standard video latent shape: [B, C, F, H, W]
        correlated_noise = correlated_noise.permute(0, 1, 4, 2, 3).contiguous()
        return correlated_noise
