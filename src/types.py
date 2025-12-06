# types.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence


class AudioFormat(Enum):
    M4A = "m4a"
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"


@dataclass(frozen=True, slots=True)
class DownloadConfig:
    output_dir: str
    audio_format: AudioFormat = AudioFormat.WAV
    filename_template: str = "%(title)s.%(ext)s"
    embed_thumbnail: bool = True
    add_metadata: bool = True
    restrict_filenames: bool = True
    quiet: bool = False
    noplaylist: bool = True


@dataclass(frozen=True, slots=True)
class AudioMeta:
    title: str
    thumbnail_url: str
    path: Path


UrlList = Sequence[str]
