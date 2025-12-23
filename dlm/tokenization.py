# dlm/tokenization.py
from enum import Enum

class VocalTokenType(str, Enum):
    CLICK = "CLICK"
    WHISTLE = "WHISTLE"
    BURST = "BURST"
    NOISE = "NOISE"

class ExpressiveMode(str, Enum):
    NEUTRAL = "NEUTRAL"
    EXCITED_EXPLANATORY = "EXCITED_EXPLANATORY"
    EXCITED_PARENTAL_EXPLANATORY = "EXCITED_PARENTAL_EXPLANATORY"

class VocalToken:
    def __init__(self, token_type, cluster_id, mode: ExpressiveMode, duration, features):
        self.token_type = token_type
        self.cluster_id = cluster_id
        self.mode = mode
        self.duration = duration
        self.features = features  # embedding or feature vector
