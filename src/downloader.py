# src/downloader.py
import yt_dlp
from typing import Sequence
from .types import DownloadConfig, AudioMeta
from .config import build_yt_dlp_options


def download_audio(urls: Sequence[str], config: DownloadConfig) -> list[AudioMeta]:
    """
    Baixa áudios do YouTube em WAV e retorna metadados (título, thumbnail).
    Função pura: não muta estado global.
    """
    if not urls:
        print("Nenhum link fornecido para download.")
        return []
    options = build_yt_dlp_options(config)
    metas: list[AudioMeta] = []
    with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore
        for url in urls:
            info = ydl.extract_info(url, download=True)
            metas.append(
                AudioMeta(
                    title=info.get("title", "unknown"),  # type: ignore
                    thumbnail_url=info.get("thumbnail", ""),  # type: ignore
                )
            )
    return metas
