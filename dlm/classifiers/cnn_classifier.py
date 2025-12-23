# dlm/classifiers/cnn_classifier.py
import torch
import torch.nn as nn

class DolphinCNNClassifier(nn.Module):
    def __init__(self, n_mels=64, n_classes=4):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Linear(32 * (n_mels // 4) *  (100 // 4), 128),  # 100 = example time frames
            nn.ReLU(),
            nn.Linear(128, n_classes),
        )

    def forward(self, x):
        # x: (batch, 1, n_mels, T)
        h = self.conv(x)
        h = h.view(h.size(0), -1)
        return self.fc(h)
