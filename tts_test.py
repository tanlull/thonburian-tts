from flowtts.inference import FlowTTSPipeline, ModelConfig, AudioConfig
import torch

# Configure F5-TTS model
model_config = ModelConfig(
    language="th",
    model_type="F5",
    checkpoint="hf://biodatlab/ThonburianTTS/megaF5/mega_f5_last.safetensors",
    vocab_file="hf://biodatlab/ThonburianTTS/megaF5/mega_vocab.txt",
    vocoder="vocos",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# Basic audio settings
audio_config = AudioConfig(
    silence_threshold=-45,
    cfg_strength=2.5,
    speed=1.0
)

pipeline = FlowTTSPipeline(model_config, audio_config)