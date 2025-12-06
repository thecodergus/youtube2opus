# audio_pipeline.py
from typing import Final
from src.denoiser import denoise_wav
from src.superres import super_resolve_wav
from src.encoder import wav_to_mp3_with_thumbnail
from src.types import DownloadConfig, AudioFormat, UrlList
from src.utils import ensure_directory_exists
from src.downloader import download_audio


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


# if __name__ == "__main__":
#     # Exemplo de uso
#     process_audio_pipeline(
#         input_wav="input.wav",
#         output_mp3="output.mp3",
#         thumbnail_url="https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg",
#         title="Título da Música",
#     )


def main(
    youtube_links: UrlList, output_dir: str, audio_format: AudioFormat = AudioFormat.M4A
) -> None:
    """
    Orquestra o fluxo de validação, configuração e download.
    """
    ensure_directory_exists(output_dir)
    config = DownloadConfig(
        output_dir=output_dir,
        audio_format=audio_format,
    )
    download_audio(youtube_links, config)


if __name__ == "__main__":
    youtube_links: UrlList = [
        "https://www.youtube.com/watch?v=YLJbYcX5LWk",
        "https://www.youtube.com/watch?v=Nw1uB_ttKt8",
    ]
    output_path: str = "./output"
    main(youtube_links, output_path, audio_format=AudioFormat.MP3)
