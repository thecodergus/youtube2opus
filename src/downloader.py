# src/downloader.py
from typing import Final, Optional
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
        title = sanitize_filename(info.get("title", "audio").replace('"', ""), platform="Universal")  # type: ignore
        thumbnail_url = info.get("thumbnail", "")  # type: ignore
        audio_path: Optional[str] = None
        for i in info.get("thumbnails"):  # type: ignore
            if "filepath" in i:
                audio_path = i.get("filepath")
    return DownloadResult(
        audio_path=str(audio_path if audio_path else ""),
        title=title,  # type: ignore
        thumbnail_url=thumbnail_url.replace("\\", "/"),  # type: ignore
    )
