# downloader.py
import yt_dlp
from typing import Sequence
from .types import DownloadConfig
from config import build_yt_dlp_options


def download_audio(urls: Sequence[str], config: DownloadConfig) -> None:
    """
    Executa o download dos áudios a partir de uma lista de URLs, usando a configuração fornecida.
    """
    if not urls:
        print("Nenhum link fornecido para download.")
        return
    options = build_yt_dlp_options(config)
    with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore
        ydl.download(list(urls))
