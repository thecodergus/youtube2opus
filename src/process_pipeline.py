from typing import Sequence
from pathlib import Path
from src.downloader import download_audio
from src.denoiser import denoise_wav
from src.superres import super_resolve_wav
from src.encoder import wav_to_flac_with_thumbnail
from src.types import DownloadResult
from src.utils import ensure_directory_exists, cleanup_temp_files


def process_youtube_links(links: Sequence[str], output_dir: str) -> None:
    """
    Processa uma lista de links do YouTube:
    1. Baixa o áudio e thumbnail
    2. Aplica denoising
    3. Aplica super-resolução
    4. Salva em FLAC com thumbnail
    """
    ensure_directory_exists(output_dir)
    for url in links:
        print(f"\n🎬 Processando: {url}")
        # try:
        # 1. Download
        result: DownloadResult = download_audio(url, output_dir)
        print(f"  ⬇️  Baixado: {result.audio_path.title}")

        # 2. Denoising
        denoised_path = Path(output_dir) / f"""{result.title}_denoised.wav"""
        denoise_wav(str(result.audio_path), str(denoised_path))
        print(f"  🧹 Denoising concluído: {denoised_path.name}")

        # 3. Super-Resolução
        superres_path = Path(output_dir) / f"""{result.title}_superres.wav"""
        super_resolve_wav(str(denoised_path), str(superres_path))
        print(f"  🚀 Super-resolução concluída: {superres_path.name}")

        # 4. FLAC + Thumbnail
        flac_path = Path(output_dir) / f"{result.title}.flac"
        wav_to_flac_with_thumbnail(
            wav_path=str(superres_path),
            flac_path=str(flac_path),
            thumbnail_url=result.thumbnail_url,
            title=result.title,
        )
        print(f"  💾 FLAC salvo: {flac_path.name}")

        # Limpeza de arquivos temporários
        cleanup_temp_files([denoised_path, superres_path, result.audio_path])  # type: ignore
        # except Exception as e:
        #     print(f"❌ Erro ao processar {url}: {e}")
