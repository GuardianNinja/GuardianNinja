Dolphin Language Model (DLM)
A modular AI architecture for modeling dolphin vocal communication (clicks, whistles, burst pulses) as a language‑like system. The goal is to:

Detect and classify vocalization types from acoustic recordings.

Learn their internal structure (units, motifs, syntax‑like rules).

Map vocalization patterns to behavioral / contextual labels.

Lay groundwork for future interspecies “translation” research.

This project builds on ideas from passive acoustic monitoring, CNN‑based classification of dolphin vocalizations, and recent foundational models like DolphinGemma.

Features
Multi‑stream acoustic input:

Raw waveform or spectrograms (mel, log‑mel, or CQT).

Metadata (location, time, pod ID, context labels).

Vocalization segmentation & classification:

Detect vocal events (clicks, whistles, burst pulses) from continuous recordings.

Classify vocalization type, species, and possibly individual ID.

Language‑model core:

Sequence modeling of vocalization “tokens” using Transformer or RNN.

Support for different expressive modes (e.g., excited‑explanatory vs excited‑parental explanatory).

Context grounding:

Joint modeling of acoustics + behavior/context (e.g., hunting, play, alarm).

Extensible for “translation”:

Learn latent representations that correlate with behavioral meaning, enabling future decoding/interaction work.
