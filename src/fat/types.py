from typing import Optional, TypeAlias
from dataclasses import dataclass
from pydub import AudioSegment
from enum import Enum, auto
import numpy as np

NpArray: TypeAlias = np.ndarray


class AudioTypes(Enum):
    MP3 = auto()
    WAV = auto()
    FLAC = auto()
    OGG = auto()

    def __str__(self) -> str:
        match self:
            case self.MP3:
                return "mp3"
            case self.WAV:
                return "wav"
            case self.FLAC:
                return "flac"
            case self.OGG:
                return "ogg"
            case _:
                return "Desconhecido"


@dataclass(frozen=True)
class AudioData:
    sample_rate: int
    samples: NpArray
    bitrate: Optional[int]
    audio_segment: AudioSegment
