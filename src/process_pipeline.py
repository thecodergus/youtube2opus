from typing import Sequence
from pathlib import Path
from src.downloader import download_audio
from src.types import DownloadResult
from src.utils import ensure_directory_exists, cleanup_temp_files

from .fat.pipeline import upscale, UpscaleConfig
from .fat.types import AudioTypes
from multiprocessing import Pool
from functools import partial
from typing import Final
import requests
from mutagen.flac import FLAC, Picture
import requests
import mimetypes
import multiprocessing as mp
import cupy as cp


def process_link(link: str, output_dir: str) -> None:

    cp.fft.config.set_plan_cache_size(4)
    print(f"\n🎬 Processando: {link}")

    # Baixando mp3
    result: DownloadResult = download_audio(link, output_dir)
    print(f"  ⬇️  Baixado: {str(result.audio_path.title)}")

    # Melhorando musica
    flac_path = output_dir + "/" + f"{result.title}.flac"
    config = UpscaleConfig(
        input_file_path=result.audio_path,
        output_file_path=flac_path,
        source_format=AudioTypes.MP3,
        target_format=AudioTypes.FLAC,
        max_iterations=3_000,
        threshold_value=0.6,
        target_bitrate_kbps=1411,
        toggle_normalize=True,
        toggle_autoscale=True,
        toggle_adaptive_filter=True,
    )
    upscale(config)
    cp.fft.config.get_plan_cache().clear()
    cp.get_default_memory_pool().free_all_blocks()
    cp.cuda.Stream.null.synchronize()

    # Adicionando Thumbmail
    response: Final[requests.Response] = requests.get(result.thumbnail_url, timeout=10)
    response.raise_for_status()
    image_data: Final[bytes] = response.content
    mime_type: str = mimetypes.guess_type(result.thumbnail_url)[0] or "image/jpeg"
    flac_audio: Final[FLAC] = FLAC(flac_path)
    flac_audio["title"] = result.title
    flac_audio.clear_pictures()
    picture: Final[Picture] = Picture()
    picture.data = image_data
    picture.type = 3
    picture.mime = mime_type
    picture.desc = "Cover"
    flac_audio.add_picture(picture)
    flac_audio.save()

    # Limpeza de arquivos temporários
    cleanup_temp_files(
        [
            Path(result.audio_path),
            Path(result.audio_path.replace(".mp3", ".webp")),
        ]
    )


def process_youtube_links(links: Sequence[str], output_dir: str) -> None:
    """
    Processa uma lista de links do YouTube:
    1. Baixa o áudio e thumbnail
    2. Aplica denoising
    3. Aplica super-resolução
    4. Salva em FLAC com thumbnail
    """
    mp.set_start_method("spawn", force=True)
    ensure_directory_exists(output_dir)
    process_partial = partial(process_link, output_dir=output_dir)

    # with Pool(processes=1) as pool:
    #     pool.map(process_partial, links)
    for i in links:
        process_partial(i)
