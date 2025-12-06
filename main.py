# audio_pipeline.py
from typing import Final
from src.denoiser import denoise_wav
from src.superres import super_resolve_wav
from src.encoder import wav_to_mp3_with_thumbnail


def process_audio_pipeline(
    input_wav: str,
    output_mp3: str,
    thumbnail_url: str,
    title: str,
    temp_denoised: str = "temp_denoised.wav",
    temp_superres: str = "temp_superres.wav",
) -> None:
    """
    Pipeline: Denoising → Super-Resolução → MP3 + Thumbnail
    """
    denoise_wav(input_wav, temp_denoised)
    super_resolve_wav(temp_denoised, temp_superres)
    wav_to_mp3_with_thumbnail(temp_superres, output_mp3, thumbnail_url, title)


if __name__ == "__main__":
    # Exemplo de uso
    process_audio_pipeline(
        input_wav="input.wav",
        output_mp3="output.mp3",
        thumbnail_url="https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg",
        title="Título da Música",
    )
