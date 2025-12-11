# src/downloader.py
from typing import Final
from pathlib import Path
import yt_dlp
from src.types import DownloadResult

from pathvalidate import sanitize_filename


def download_audio(url: str, output_dir: str) -> DownloadResult:
    """
    Baixa áudio do YouTube em WAV e retorna metadados e caminho da thumbnail.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"""{output_dir}/%(title)s.%(ext)s""",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                # "preferredcodec": "wav",
                "preferredcodec": "mp3",
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
        title = sanitize_filename(info.get("title", "audio").replace('"', ""), platform="windows")  # type: ignore
        thumbnail_url = info.get("thumbnail", "")  # type: ignore
        audio_path = Path(ydl.prepare_filename(info).replace("webm", "mp3"))  # type: ignore
    return DownloadResult(
        audio_path=str(audio_path),
        title=title,  # type: ignore
        thumbnail_url=thumbnail_url.replace("\\", "/"),  # type: ignore
    )
