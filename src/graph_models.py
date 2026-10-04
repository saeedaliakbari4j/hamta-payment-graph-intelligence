"""
Graph Neural Network Models Module
Implements Multi-Head Graph Attention Network (GAT) and Graph Autoencoder (GAE)
for self-supervised payment network representation learning in pure PyTorch.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Optional
from src.config import cfg

class GraphAttentionLayer(nn.Module):
    """
    Edge-Weighted Multi-Head Graph Attention Layer (GAT).
    Fuses node attributes with topological edge affinity weights.
    """
    def __init__(self, in_features: int, out_features: int, dropout: float = 0.1, alpha: float = 0.2):
        super(GraphAttentionLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.dropout = dropout
        self.alpha = alpha

        self.W = nn.Linear(in_features, out_features, bias=False)
        self.a = nn.Parameter(torch.zeros(size=(2 * out_features, 1)))
        self.edge_bias = nn.Parameter(torch.tensor([0.5]))
        self.leaky_relu = nn.LeakyReLU(self.alpha)

        nn.init.xavier_uniform_(self.W.weight.data, gain=1.414)
        nn.init.xavier_uniform_(self.a.data, gain=1.414)

    def forward(self, h: torch.Tensor, edge_index: torch.Tensor, edge_weight: Optional[torch.Tensor] = None) -> torch.Tensor:
        num_nodes = h.size(0)
        Wh = self.W(h)  # (N, out_features)

        src, dst = edge_index[0], edge_index[1]
        
        # Concatenate source and target node projections
        edge_h = torch.cat([Wh[src], Wh[dst]], dim=1)  # (E, 2 * out_features)
        
        # Compute unnormalized attention scores
        attn_scores = self.leaky_relu(torch.matmul(edge_h, self.a).squeeze(1))  # (E,)
        
        if edge_weight is not None:
            attn_scores = attn_scores + self.edge_bias * torch.log(edge_weight + 1e-6)

        # Numerically stable edge softmax per target node
        # Exponentiate scores
        exp_scores = torch.exp(attn_scores - attn_scores.max())
        
        # Aggregate denominator per target node
        sum_exp = torch.zeros(num_nodes, device=h.device)
        sum_exp.scatter_add_(0, dst, exp_scores)
        sum_exp = sum_exp + 1e-9  # avoid zero division
        
        norm_attn = exp_scores / sum_exp[dst]
        norm_attn = F.dropout(norm_attn, p=self.dropout, training=self.training)

        # Message aggregation: weighted sum of source representations
        weighted_msgs = Wh[src] * norm_attn.unsqueeze(1)
        out = torch.zeros(num_nodes, self.out_features, device=h.device)
        out.scatter_add_(0, dst.unsqueeze(1).expand(-1, self.out_features), weighted_msgs)

        return out

class MultiHeadGAT(nn.Module):
    """
    Multi-Head GAT with residual skip connection and feature reconstruction decoder.
    """
    def __init__(self, in_features: int, hidden_dim: int, embed_dim: int, num_heads: int = 4, dropout: float = 0.1):
        super(MultiHeadGAT, self).__init__()
        self.num_heads = num_heads
        head_dim = hidden_dim // num_heads

        self.heads = nn.ModuleList([
            GraphAttentionLayer(in_features, head_dim, dropout=dropout)
            for _ in range(num_heads)
        ])
        
        self.out_head = GraphAttentionLayer(hidden_dim, embed_dim, dropout=dropout)
        self.proj_residual = nn.Linear(in_features, hidden_dim) if in_features != hidden_dim else nn.Identity()
        self.layer_norm1 = nn.LayerNorm(hidden_dim)
        self.layer_norm2 = nn.LayerNorm(embed_dim)

        # Attribute Reconstruction Decoder
        self.attribute_decoder = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, in_features)
        )

    def encode(self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Multi-head attention aggregation
        head_outs = [head(x, edge_index, edge_weight) for head in self.heads]
        h1 = torch.cat(head_outs, dim=1)
        h1 = F.elu(h1 + self.proj_residual(x))
        h1 = self.layer_norm1(h1)

        # Bottleneck embedding layer
        z = self.out_head(h1, edge_index, edge_weight)
        z = self.layer_norm2(z)
        return z

    def decode_topology(self, z: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Normalized cosine affinity topological decoder."""
        src, dst = edge_index[0], edge_index[1]
        z_src = F.normalize(z[src], p=2, dim=1)
        z_dst = F.normalize(z[dst], p=2, dim=1)
        sim = torch.sum(z_src * z_dst, dim=1)
        prob = (sim + 1.0) / 2.0
        return torch.clamp(prob, 1e-6, 1.0 - 1e-6)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.encode(x, edge_index, edge_weight)
        x_recon = self.attribute_decoder(z)
        return z, x_recon

class PaymentGraphModelTrainer:
    """
    Self-supervised training orchestrator for Graph Autoencoders on payment graphs.
    """
    def __init__(self, in_features: int, config=cfg):
        self.cfg = config
        torch.manual_seed(self.cfg.SEED)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = MultiHeadGAT(
            in_features=in_features,
            hidden_dim=self.cfg.GNN_HIDDEN_DIM,
            embed_dim=self.cfg.EMBEDDING_DIM,
            num_heads=self.cfg.GNN_HEADS,
            dropout=self.cfg.DROPOUT
        ).to(self.device)

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.cfg.LEARNING_RATE,
            weight_decay=self.cfg.WEIGHT_DECAY
        )

    def sample_negative_edges(self, edge_index: torch.Tensor, num_nodes: int, num_neg: int) -> torch.Tensor:
        """Fast negative edge sampling for link reconstruction."""
        neg_src = torch.randint(0, num_nodes, (num_neg,), device=self.device)
        neg_dst = torch.randint(0, num_nodes, (num_neg,), device=self.device)
        return torch.stack([neg_src, neg_dst], dim=0)

    def train_embeddings(
        self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: torch.Tensor
    ) -> Tuple[np.ndarray, list]:
        """
        Trains GNN with joint link prediction loss and node attribute reconstruction loss.
        """
        x = x.to(self.device)
        edge_index = edge_index.to(self.device)
        edge_weight = edge_weight.to(self.device)
        num_nodes = x.size(0)
        num_edges = edge_index.size(1)

        self.model.train()
        loss_history = []

        print(f"[ModelTrainer] Training Graph Autoencoder for {self.cfg.EPOCHS} epochs on {self.device}...")

        for epoch in range(1, self.cfg.EPOCHS + 1):
            self.optimizer.zero_grad()
            
            # Forward pass
            z, x_recon = self.model(x, edge_index, edge_weight)

            # 1. Topological Reconstruction Loss (Positive Edges)
            pos_preds = self.model.decode_topology(z, edge_index)
            pos_loss = F.binary_cross_entropy(pos_preds, torch.ones_like(pos_preds))

            # 2. Topological Reconstruction Loss (Negative Edges)
            neg_edges = self.sample_negative_edges(edge_index, num_nodes, num_edges // 2)
            neg_preds = self.model.decode_topology(z, neg_edges)
            neg_loss = F.binary_cross_entropy(neg_preds, torch.zeros_like(neg_preds))

            # 3. Node Attribute Reconstruction Regularization
            attr_loss = F.mse_loss(x_recon, x)

            total_loss = pos_loss + neg_loss + 0.3 * attr_loss
            total_loss.backward()
            
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.5)
            self.optimizer.step()

            loss_val = total_loss.item()
            loss_history.append(loss_val)

            if epoch % 10 == 0 or epoch == self.cfg.EPOCHS:
                print(f"  Epoch {epoch:03d}/{self.cfg.EPOCHS:03d} | Total Loss: {loss_val:.4f} "
                      f"(Pos: {pos_loss.item():.4f}, Neg: {neg_loss.item():.4f}, Attr: {attr_loss.item():.4f})")

        self.model.eval()
        with torch.no_grad():
            final_embeddings, _ = self.model(x, edge_index, edge_weight)
            final_embeddings = final_embeddings.cpu().numpy()

        return final_embeddings, loss_history

if __name__ == "__main__":
    from src.graph_builder import PaymentGraphBuilder
    import pandas as pd
    df_tx = pd.read_csv(cfg.DATA_PATH)
    builder = PaymentGraphBuilder()
    G, x, edge_index, edge_weight, cust_list = builder.build_customer_co_occurrence_graph(df_tx)
    
    trainer = PaymentGraphModelTrainer(in_features=x.size(1))
    embeddings, history = trainer.train_embeddings(x, edge_index, edge_weight)
    print("Learned embeddings shape:", embeddings.shape)
