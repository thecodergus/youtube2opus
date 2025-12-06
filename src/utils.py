# file_utils.py
import os
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs, urlencode


def ensure_directory_exists(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def cleanup_temp_files(paths: list[Path]) -> None:
    for p in paths:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass


def clean_youtube_url(url: str, keep_timestamp: bool = True) -> str | None:
    """
    Recebe um link do YouTube, verifica se é válido e retorna o link limpo (apenas do vídeo).
    Remove parâmetros de playlist, tracking, embed, etc.
    Se keep_timestamp=True, preserva t/start/end se presentes.
    Retorna None se não for um link válido de vídeo.
    """
    # Regex abrangente para todos os formatos
    regex = re.compile(
        r"""(?x)
        (?:https?://)?(?:www\.)?(?:m\.)?
        (?:youtube\.com|youtu\.be|youtube-nocookie\.com)
        (?:
            (?:/watch\?(?:.*&)?v=)|
            (?:/embed/)|
            (?:/v/)|
            (?:/shorts/)|
            (?:/live/)|
            (?:/)?  # para youtu.be/
        )
        ([\w-]{11})
        (?:[^\w-]|$)
        """
    )
    match = regex.search(url)
    video_id = None

    if match:
        video_id = match.group(1)
    else:
        # fallback: parsing query string
        parsed = urlparse(url)
        if parsed.hostname and "youtube" in parsed.hostname:
            qs = parse_qs(parsed.query)
            if "v" in qs and len(qs["v"][0]) == 11:
                video_id = qs["v"][0]

    if not (video_id and len(video_id) == 11):
        return None  # Não é um link válido de vídeo

    # Parse parâmetros para preservar timestamp se desejado
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    params = {}
    if keep_timestamp:
        for key in ["t", "start", "end"]:
            if key in qs:
                params[key] = qs[key][0]
        # Também suporta fragmento #t=...
        if parsed.fragment and parsed.fragment.startswith("t="):
            params["t"] = parsed.fragment[2:]

    # Monta URL limpa
    base = f"https://www.youtube.com/watch?v={video_id}"
    if params:
        base += "&" + urlencode(params)
    return base
