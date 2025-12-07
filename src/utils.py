# file_utils.py
import os
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Final


def ensure_directory_exists(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def cleanup_temp_files(paths: list[Path]) -> None:
    for p in paths:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass


# youtube_url_cleaner.py


class InvalidYouTubeVideoUrl(Exception):
    """Exceção lançada quando a URL não é um vídeo válido do YouTube."""


_YOUTUBE_DOMAINS: Final[set[str]] = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
    "music.youtube.com",
}

_YOUTUBE_ID_REGEX: Final[re.Pattern[str]] = re.compile(
    r"""(?x)
    (?:https?://)?(?:www\.)?(?:m\.)?
    (?:youtube\.com|youtu\.be|youtube-nocookie\.com|music\.youtube\.com)
    (?:
        (?:/watch\?(?:.*&)?v=)|
        (?:/embed/)|
        (?:/v/)|
        (?:/shorts/)|
        (?:/live/)|
        (?:/)?  # para youtu.be/
    )
    ([A-Za-z0-9_-]{11})
    (?:[^\w-]|$)
    """
)


def _is_youtube_domain(url: str) -> bool:
    """Verifica se a URL pertence a um domínio do YouTube suportado."""
    parsed = urlparse(url if url.startswith("http") else "https://" + url)
    hostname = (parsed.hostname or "").lower()
    return any(
        hostname == domain or hostname.endswith("." + domain)
        for domain in _YOUTUBE_DOMAINS
    )


def _extract_video_id(url: str) -> str | None:
    """Extrai o ID do vídeo de qualquer formato de URL do YouTube."""
    match = _YOUTUBE_ID_REGEX.search(url)
    if match:
        return match.group(1)
    parsed = urlparse(url if url.startswith("http") else "https://" + url)
    path_parts = parsed.path.strip("/").split("/")
    match path_parts:
        case ["embed", vid] if len(vid) == 11 and re.fullmatch(
            r"[A-Za-z0-9_-]{11}", vid
        ):
            return vid
        case ["shorts", vid] if len(vid) == 11 and re.fullmatch(
            r"[A-Za-z0-9_-]{11}", vid
        ):
            return vid
        case ["live", vid] if len(vid) == 11 and re.fullmatch(
            r"[A-Za-z0-9_-]{11}", vid
        ):
            return vid
        case [vid] if len(vid) == 11 and re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            return vid
    qs = parse_qs(parsed.query)
    v = qs.get("v", [""])
    if v and len(v[0]) == 11 and re.fullmatch(r"[A-Za-z0-9_-]{11}", v[0]):
        return v[0]
    return None


def clean_youtube_url(url: str) -> str:
    """
    Limpa uma URL de vídeo do YouTube, removendo parâmetros supérfluos.
    Retorna a URL canônica do vídeo.
    Lança InvalidYouTubeVideoUrl se a URL não for válida para vídeo.
    """
    if not url or not isinstance(url, str):
        raise InvalidYouTubeVideoUrl("URL vazia ou inválida")
    if not _is_youtube_domain(url):
        parsed = urlparse(url if url.startswith("http") else "https://" + url)
        raise InvalidYouTubeVideoUrl(
            f"Domínio não é do YouTube: {parsed.hostname or url}"
        )
    video_id = _extract_video_id(url)
    if not video_id:
        raise InvalidYouTubeVideoUrl("Não foi possível extrair ID do vídeo")
    return f"https://www.youtube.com/watch?v={video_id}"
