# types.py
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class AudioFormat(Enum):
    M4A = "m4a"
    MP3 = "mp3"
    WAV = "wav"


@dataclass(frozen=True, slots=True)
class DownloadConfig:
    output_dir: str
    audio_format: AudioFormat = AudioFormat.M4A
    filename_template: str = "%(title)s.%(ext)s"
    embed_thumbnail: bool = True
    add_metadata: bool = True
    restrict_filenames: bool = True
    quiet: bool = False
    noplaylist: bool = True


UrlList = Sequence[str]
