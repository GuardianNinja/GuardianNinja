# dlm/features.py
import librosa
import numpy as np

def compute_logmel_spectrogram(waveform, sr, n_mels=64, hop_length=256, win_length=1024):
    spec = librosa.feature.melspectrogram(
        y=waveform,
        sr=sr,
        n_mels=n_mels,
        hop_length=hop_length,
        win_length=win_length
    )
    logspec = librosa.power_to_db(spec + 1e-10)
    return logspec.astype(np.float32)
