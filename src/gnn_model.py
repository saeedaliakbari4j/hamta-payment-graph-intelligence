"""
Higher-Order Curvature-Attentive Neural Autoencoder (HG-CAN) Module
Novel Geometric Deep Learning Architecture for Payment Transactional Intelligence.
Modulates Multi-Head Graph Attention via Discrete Forman-Ricci Topological Curvature.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
from typing import Dict, Tuple
from src.config import cfg

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class CurvatureAttentiveLayer(nn.Module):
    """
    Higher-order Graph Attention Layer with Discrete Ricci Curvature Modulation.
    alpha_ij = Softmax_j(LeakyReLU(a^T [W h_i || W h_j] + gamma_w * ln(w_ij) + gamma_c * tanh(kappa_ij)))
    """
    def __init__(self, in_features: int, out_features: int, heads: int = 4, dropout: float = 0.1):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.heads = heads
        self.head_dim = out_features // heads

        self.W = nn.Linear(in_features, heads * self.head_dim, bias=False)
        self.a_src = nn.Parameter(torch.empty(size=(heads, self.head_dim, 1)))
        self.a_dst = nn.Parameter(torch.empty(size=(heads, self.head_dim, 1)))
        
        # Learnable topological modulation parameters
        self.gamma_weight = nn.Parameter(torch.tensor(0.5, dtype=torch.float32))
        self.gamma_curvature = nn.Parameter(torch.tensor(0.3, dtype=torch.float32))

        self.leaky_relu = nn.LeakyReLU(0.2)
        self.dropout = nn.Dropout(dropout)

        # Initialize parameters
        nn.init.xavier_uniform_(self.W.weight)
        nn.init.xavier_uniform_(self.a_src)
        nn.init.xavier_uniform_(self.a_dst)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: torch.Tensor, edge_curvature: torch.Tensor) -> torch.Tensor:
        num_nodes = x.size(0)
        # Linear projection: [N, heads, head_dim]
        h = self.W(x).view(num_nodes, self.heads, self.head_dim)

        src, dst = edge_index[0], edge_index[1]

        # Compute attentional self and neighbor components
        # h[src]: [E, heads, head_dim]
        attn_src = (h[src] * self.a_src.squeeze(-1)).sum(dim=-1) # [E, heads]
        attn_dst = (h[dst] * self.a_dst.squeeze(-1)).sum(dim=-1) # [E, heads]
        attn = attn_src + attn_dst

        # Curvature & Edge Weight Geometric Modulation
        w_term = self.gamma_weight * torch.log(edge_weight.clamp(min=1e-6)).unsqueeze(-1)
        curv_term = self.gamma_curvature * torch.tanh(edge_curvature).unsqueeze(-1)

        raw_scores = self.leaky_relu(attn + w_term + curv_term)

        # Numerically stable softmax over incoming edges
        # We perform edge-wise softmax grouping by destination node
        max_scores = torch.zeros(num_nodes, self.heads, device=x.device).scatter_reduce(
            0, dst.unsqueeze(-1).expand(-1, self.heads), raw_scores, reduce="amax", include_self=False
        )
        exp_scores = torch.exp(raw_scores - max_scores[dst])
        denom = torch.zeros(num_nodes, self.heads, device=x.device).scatter_add(
            0, dst.unsqueeze(-1).expand(-1, self.heads), exp_scores
        ) + 1e-12

        alpha = self.dropout(exp_scores / denom[dst]) # [E, heads]

        # Message aggregation: [E, heads, head_dim] * [E, heads, 1]
        msg = h[src] * alpha.unsqueeze(-1)

        # Scatter add into destination nodes
        out = torch.zeros(num_nodes, self.heads, self.head_dim, device=x.device)
        dst_expanded = dst.view(-1, 1, 1).expand(-1, self.heads, self.head_dim)
        out.scatter_add_(0, dst_expanded, msg)

        # Concatenate multi-head outputs: [N, heads * head_dim]
        return out.view(num_nodes, self.heads * self.head_dim)


class HGCANEncoder(nn.Module):
    """Two-layer Curvature-Attentive Encoder with Residual Connection."""
    def __init__(self, in_dim: int = 8, hidden_dim: int = 64, out_dim: int = 32, heads: int = 4, dropout: float = 0.1):
        super().__init__()
        self.conv1 = CurvatureAttentiveLayer(in_dim, hidden_dim, heads=heads, dropout=dropout)
        self.conv2 = CurvatureAttentiveLayer(hidden_dim, out_dim, heads=heads, dropout=dropout)
        self.res_proj = nn.Linear(in_dim, out_dim)
        self.layer_norm = nn.LayerNorm(out_dim)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: torch.Tensor, edge_curvature: torch.Tensor) -> torch.Tensor:
        res = self.res_proj(x)
        h1 = F.elu(self.conv1(x, edge_index, edge_weight, edge_curvature))
        h2 = self.conv2(h1, edge_index, edge_weight, edge_curvature)
        out = self.layer_norm(h2 + res)
        return out


class AttributeDecoder(nn.Module):
    """Reconstructs intrinsic 8-dimensional node attributes from latent embeddings."""
    def __init__(self, in_dim: int = 32, hidden_dim: int = 64, out_dim: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, out_dim)
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


class HGCANAutoencoder(nn.Module):
    """Complete Self-Supervised Curvature-Attentive Graph Autoencoder."""
    def __init__(self, in_dim: int = 8, hidden_dim: int = 64, out_dim: int = 32, heads: int = 4, dropout: float = 0.1):
        super().__init__()
        self.encoder = HGCANEncoder(in_dim, hidden_dim, out_dim, heads, dropout)
        self.attr_decoder = AttributeDecoder(out_dim, hidden_dim, in_dim)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: torch.Tensor, edge_curvature: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x, edge_index, edge_weight, edge_curvature)
        x_recon = self.attr_decoder(z)
        return z, x_recon

    def compute_link_loss(self, z: torch.Tensor, pos_edge_index: torch.Tensor, num_neg_samples: int = None) -> torch.Tensor:
        """Binary cross-entropy loss on positive and negative edge reconstruction."""
        src_pos, dst_pos = pos_edge_index[0], pos_edge_index[1]
        pos_scores = (z[src_pos] * z[dst_pos]).sum(dim=-1)

        # Negative sampling
        num_neg = pos_edge_index.size(1) if num_neg_samples is None else num_neg_samples
        neg_src = torch.randint(0, z.size(0), (num_neg,), device=z.device)
        neg_dst = torch.randint(0, z.size(0), (num_neg,), device=z.device)
        neg_scores = (z[neg_src] * z[neg_dst]).sum(dim=-1)

        pos_loss = F.binary_cross_entropy_with_logits(pos_scores, torch.ones_like(pos_scores))
        neg_loss = F.binary_cross_entropy_with_logits(neg_scores, torch.zeros_like(neg_scores))
        return (pos_loss + neg_loss) / 2.0


def train_model(graph_data: Dict, epochs: int = cfg.EPOCHS) -> Tuple[HGCANAutoencoder, torch.Tensor]:
    """Train the HG-CAN model end-to-end and extract continuous latent representations."""
    torch.manual_seed(cfg.SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    x = graph_data["x"].to(device)
    edge_index = graph_data["edge_index"].to(device)
    edge_weight = graph_data["edge_weight"].to(device)
    edge_curvature = graph_data["edge_curvature"].to(device)

    model = HGCANAutoencoder(
        in_dim=x.size(1),
        hidden_dim=cfg.GNN_HIDDEN_DIM,
        out_dim=cfg.EMBEDDING_DIM,
        heads=cfg.GNN_HEADS,
        dropout=cfg.DROPOUT
    ).to(device)

    optimizer = Adam(model.parameters(), lr=cfg.LEARNING_RATE, weight_decay=cfg.WEIGHT_DECAY)

    print(f"[HG-CAN] Training Curvature-Attentive Neural Autoencoder for {epochs} epochs on {device}...")
    model.train()

    lambda_attr = 0.5
    lambda_curv = 0.2

    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        z, x_recon = model(x, edge_index, edge_weight, edge_curvature)

        # 1. Link reconstruction loss
        loss_link = model.compute_link_loss(z, edge_index)

        # 2. Attribute reconstruction loss
        loss_attr = F.mse_loss(x_recon, x)

        # 3. Curvature-contrastive regularization
        # Positive curvature edges should have high cosine similarity; negative bridge edges should have lower similarity
        src, dst = edge_index[0], edge_index[1]
        pair_sim = F.cosine_similarity(z[src], z[dst], dim=-1)
        curv_target = torch.sigmoid(edge_curvature) # Map curvature to [0, 1]
        loss_curv = F.mse_loss(pair_sim, curv_target)

        loss_total = loss_link + (lambda_attr * loss_attr) + (lambda_curv * loss_curv)
        loss_total.backward()
        optimizer.step()

        if epoch % 15 == 0 or epoch == epochs:
            print(f"  Epoch {epoch:02d}/{epochs:02d} | Total Loss: {loss_total.item():.4f} (Link: {loss_link.item():.4f}, Attr: {loss_attr.item():.4f}, Curv: {loss_curv.item():.4f})")

    model.eval()
    with torch.no_grad():
        final_embeddings, _ = model(x, edge_index, edge_weight, edge_curvature)

    return model, final_embeddings.cpu()


if __name__ == "__main__":
    from src.graph_builder import HypergraphBuilder
    builder = HypergraphBuilder()
    data = builder.build_topological_network()
    model, embeddings = train_model(data, epochs=45)
    print("Training finished! Learned embedding matrix shape:", embeddings.shape)
