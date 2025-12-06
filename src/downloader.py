# src/downloader.py
from typing import Final
from pathlib import Path
import yt_dlp
from src.types import DownloadResult


def download_audio(url: str, output_dir: str) -> DownloadResult:
    """
    Baixa áudio do YouTube em WAV e retorna metadados e caminho da thumbnail.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
        "writethumbnail": True,
        "quiet": True,
        "noplaylist": True,
        "restrictfilenames": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "audio")
        thumbnail_url = info.get("thumbnail", "")
        audio_path = Path(f"{output_dir}/{title}.wav")
    return DownloadResult(
        audio_path=str(audio_path),
        title=title,  # type: ignore
        thumbnail_url=thumbnail_url,  # type: ignore
    )
