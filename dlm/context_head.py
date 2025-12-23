# dlm/context_head.py
import torch.nn as nn

class ContextHead(nn.Module):
    def __init__(self, d_model=256, n_contexts=10):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Linear(128, n_contexts)
        )

    def forward(self, h_seq):
        """
        h_seq: (batch, seq_len, d_model)
        Returns context logits per time step or pooled.
        """
        # e.g., pool over time
        h_pool = h_seq.mean(dim=1)
        return self.fc(h_pool)
