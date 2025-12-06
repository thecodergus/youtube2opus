# encoder.py
from typing import Final
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC, TIT2
from mutagen.id3._util import error
import requests
from mutagen.flac import FLAC, Picture
import requests
import mimetypes


def wav_to_mp3_with_thumbnail(
    wav_path: str, mp3_path: str, thumbnail_url: str, title: str
) -> None:
    """
    Converte WAV para MP3 320kbps e embute thumbnail e título usando mutagen.
    """
    # Conversão WAV → MP3
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3", bitrate="320k")

    # Download da thumbnail
    response = requests.get(thumbnail_url, timeout=10)
    response.raise_for_status()
    image_data = response.content

    # Adiciona tags ID3 (capa e título)
    audio_mp3 = MP3(mp3_path, ID3=ID3)
    try:
        audio_mp3.add_tags()
    except error:
        pass  # Tags já existem

    audio_mp3.add_tags(
        APIC(
            encoding=3,  # UTF-8
            mime="image/jpeg",  # ou "image/png" conforme thumbnail
            type=3,  # Cover (front)
            desc="Cover",
            data=image_data,
        )
    )
    audio_mp3.add_tags(TIT2(encoding=3, text=title))
    audio_mp3.save()


def wav_to_flac_with_thumbnail(
    wav_path: str, flac_path: str, thumbnail_url: str, title: str
) -> None:
    """
    Converte WAV para FLAC, embutindo título e thumbnail.
    """
    # 1. WAV → FLAC
    audio: Final[AudioSegment] = AudioSegment.from_wav(wav_path)
    audio.export(flac_path, format="flac")

    # 2. Download thumbnail
    response: Final[requests.Response] = requests.get(thumbnail_url, timeout=10)
    response.raise_for_status()
    image_data: Final[bytes] = response.content
    mime_type: str = mimetypes.guess_type(thumbnail_url)[0] or "image/jpeg"

    # 3. Metadados FLAC
    flac_audio: Final[FLAC] = FLAC(flac_path)
    flac_audio["title"] = title
    flac_audio.clear_pictures()
    picture: Final[Picture] = Picture()
    picture.data = image_data
    picture.type = 3  # Cover (front)
    picture.mime = mime_type
    picture.desc = "Cover"
    flac_audio.add_picture(picture)
    flac_audio.save()
