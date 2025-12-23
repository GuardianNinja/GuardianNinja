# scripts/train_lm.py
import torch
from torch.utils.data import DataLoader
from dlm.models.transformer_lm import DolphinTransformerLM
from dlm.context_head import ContextHead

def train_language_model(train_dataset, val_dataset, vocab_size, mode_size, n_contexts, epochs=50):
    lm = DolphinTransformerLM(vocab_size=vocab_size, mode_size=mode_size)
    ctx_head = ContextHead(d_model=256, n_contexts=n_contexts)

    params = list(lm.parameters()) + list(ctx_head.parameters())
    optimizer = torch.optim.Adam(params, lr=1e-4)
    criterion_lm = torch.nn.CrossEntropyLoss()
    criterion_mode = torch.nn.CrossEntropyLoss()
    criterion_ctx = torch.nn.CrossEntropyLoss()

    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

    for epoch in range(epochs):
        lm.train()
        ctx_head.train()
        for batch in train_loader:
            token_ids, mode_ids, next_token_ids, context_ids = batch
            logits_tokens, logits_modes = lm(token_ids, mode_ids)
            ctx_logits = ctx_head(logits_tokens)  # or pass transformer states directly

            loss_lm = criterion_lm(
                logits_tokens[:, :-1].reshape(-1, vocab_size),
                next_token_ids[:, 1:].reshape(-1)
            )
            loss_mode = criterion_mode(
                logits_modes.reshape(-1, mode_size),
                mode_ids.reshape(-1)
            )
            loss_ctx = criterion_ctx(ctx_logits, context_ids)

            loss = loss_lm + loss_mode + loss_ctx

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # TODO: add validation and logging
