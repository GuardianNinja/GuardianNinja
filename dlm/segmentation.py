# dlm/segmentation.py
import numpy as np

def detect_events(waveform, sr, energy_thresh=0.01, min_silence=0.05):
    """
    Simple energy-based event detection.
    Returns list of (start_time, end_time) in seconds.
    """
    # TODO: implement short-time energy & thresholding
    raise NotImplementedError

def extract_clips(waveform, sr, events, padding=0.01):
    """
    Slice waveform into clips around detected events.
    """
    clips = []
    for start, end in events:
        s = max(0, int((start - padding) * sr))
        e = min(len(waveform), int((end + padding) * sr))
        clips.append(waveform[s:e])
    return clips
