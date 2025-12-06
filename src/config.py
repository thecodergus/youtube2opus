# src/config.py
import os
from .types import DownloadConfig, AudioFormat


def build_yt_dlp_options(config: DownloadConfig) -> dict[str, object]:
    """
    Função pura: constrói o dicionário de opções do yt-dlp a partir da configuração tipada.
    """
    return {
        "format": f"bestaudio[ext={config.audio_format.value}]/bestaudio/best",
        "outtmpl": os.path.join(config.output_dir, config.filename_template),
        "writethumbnail": config.embed_thumbnail,
        "embedthumbnail": config.embed_thumbnail,
        "addmetadata": config.add_metadata,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": config.audio_format.value,
                "preferredquality": "0",
            },
            {"key": "EmbedThumbnail"},
            {"key": "FFmpegMetadata"},
        ],
        "noplaylist": config.noplaylist,
        "quiet": config.quiet,
        "restrictfilenames": config.restrict_filenames,
    }
