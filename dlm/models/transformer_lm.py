# dlm/models/transformer_lm.py
import torch
import torch.nn as nn

class DolphinTransformerLM(nn.Module):
    def __init__(self, vocab_size, mode_size, d_model=256, n_heads=4, num_layers=4, max_len=512):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.mode_emb = nn.Embedding(mode_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)

        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=n_heads, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.lm_head = nn.Linear(d_model, vocab_size)
        self.mode_head = nn.Linear(d_model, mode_size)

    def forward(self, token_ids, mode_ids):
        """
        token_ids: (batch, seq_len)
        mode_ids:  (batch, seq_len)
        """
        b, t = token_ids.size()
        pos = torch.arange(t, device=token_ids.device).unsqueeze(0).expand(b, t)

        x = self.token_emb(token_ids) + self.mode_emb(mode_ids) + self.pos_emb(pos)
        h = self.transformer(x)

        logits_tokens = self.lm_head(h)      # next-token logits
        logits_modes = self.mode_head(h)     # mode prediction logits
        return logits_tokens, logits_modes
