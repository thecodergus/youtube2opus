import os
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from .types import AudioData, NpArray, AudioTypes


def read_audio(file_path: str, fmt: AudioTypes) -> AudioData:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    extra_params = ["-drc_scale", "0"]
    audio = AudioSegment.from_file(file_path, format=str(fmt), parameters=extra_params)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    sample_rate = audio.frame_rate

    match fmt:
        case AudioTypes.MP3:
            bitrate = MP3(file_path).info.bitrate  # type: ignore
        case AudioTypes.FLAC:
            bitrate = FLAC(file_path).info.bitrate
        case AudioTypes.OGG:
            bitrate = OggVorbis(file_path).info.bitrate  # type: ignore
        case AudioTypes.WAV:
            bitrate = WAVE(file_path).info.bitrate
        case _:
            duration = len(audio) / 1000.0
            bitrate = int((len(samples) * 8) / duration) if duration > 0 else None

    if audio.channels == 2:
        samples = samples.reshape((-1, 2))

    return AudioData(
        sample_rate=sample_rate, samples=samples, bitrate=bitrate, audio_segment=audio
    )


def write_audio(
    file_path: str, sample_rate: int, data: NpArray, fmt: AudioTypes
) -> None:
    match fmt:
        case AudioTypes.FLAC:
            sf.write(
                file_path,
                data.astype(np.float32),
                sample_rate,
                format="FLAC",
                subtype="PCM_24",
                compression_level=1,
            )
        case AudioTypes.WAV:
            sf.write(
                file_path,
                data.astype(np.float32),
                sample_rate,
                format="WAV",
                subtype="PCM_32",
            )
        case _:
            raise ValueError(f"Formato de saída não suportado: {fmt}")
