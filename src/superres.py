# superres.py
from typing import Final
from audiosr import build_model, super_resolution, save_wave


def super_resolve_wav(
    input_wav: str, output_wav: str, model_name: str = "basic", device: str = "cpu"
) -> None:
    """
    Aplica super-resolução de áudio usando AudioSR.
    - model_name: "basic" (música) ou "speech" (voz)
    - device: "cuda" ou "cpu"
    """
    model = build_model(model_name=model_name, device=device)
    waveform = super_resolution(
        model,
        input_wav,
        seed=42,
        guidance_scale=3.5,
        ddim_steps=50,
        latent_t_per_second=25,
    )
    save_wave(
        waveform,
        inputpath=input_wav,
        savepath=".",
        name=output_wav.removesuffix(".wav"),
        samplerate=48_000,
    )
