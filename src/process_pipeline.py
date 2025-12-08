from typing import Sequence
from pathlib import Path
from src.downloader import download_audio
from src.encoder import wav_to_flac_with_thumbnail
from src.types import DownloadResult
from src.utils import ensure_directory_exists, cleanup_temp_files
from fat_llama.audio_fattener.feed import upscale
from multiprocessing import Pool
from functools import partial


def process_link(link: str, output_dir: str) -> None:
    print(f"\n🎬 Processando: {link}")
    # try:
    # Download
    result: DownloadResult = download_audio(link, output_dir)
    print(f"  ⬇️  Baixado: {result.audio_path.title}")
    flac_path = Path(output_dir + "/" + f"{result.title}.flac")
    upscale(
        input_file_path=str(result.audio_path),
        output_file_path=flac_path,
        source_format="mp3",
        target_format="flac",
        max_iterations=1_000,
        threshold_value=0.6,
        target_bitrate_kbps=1411,
        toggle_normalize=True,
        toggle_autoscale=True,
        toggle_adaptive_filter=True,
    )

    # # FLAC + Thumbnail
    # flac_path = Path(output_dir + "/" + f"{result.title}.flac")
    # wav_to_flac_with_thumbnail(
    #     wav_path=str(result.audio_path),
    #     flac_path=str(flac_path),
    #     thumbnail_url=result.thumbnail_url,
    #     title=result.title,
    # )
    # print(f"  💾 FLAC salvo: {flac_path.name}")

    # Limpeza de arquivos temporários
    cleanup_temp_files(
        [
            Path(result.audio_path),
            Path(result.audio_path),
            Path(result.audio_path.replace(".wav", ".webp")),
        ]
    )
    # except Exception as e:
    #     print(f"❌ Erro ao processar {url}: {e}")


def process_youtube_links(links: Sequence[str], output_dir: str) -> None:
    """
    Processa uma lista de links do YouTube:
    1. Baixa o áudio e thumbnail
    2. Aplica denoising
    3. Aplica super-resolução
    4. Salva em FLAC com thumbnail
    """
    ensure_directory_exists(output_dir)
    process_partial = partial(process_link, output_dir=output_dir)

    with Pool(processes=8) as pool:
        pool.map(process_partial, links)
