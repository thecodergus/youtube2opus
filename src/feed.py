from typing import Optional, Union, TypeAlias, Tuple, Callable, Sequence, Any, cast
from dataclasses import dataclass, field
import numpy as np
import cupy as cp
from pydub import AudioSegment
import soundfile as sf
import os
import logging
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from enum import Enum, auto
from functools import partial
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Lock
from contextlib import contextmanager
import cupy as cp
import gc


class AudioTypes(Enum):
    MP3 = auto()
    WAV = auto()
    FLAC = auto()
    OGG = auto()


@contextmanager
def gpu_memory_scope(*arrays: cp.ndarray):
    """
    Context manager para liberar arrays CuPy e limpar o memory pool ao sair do contexto.
    """
    try:
        yield
    finally:
        for arr in arrays:
            try:
                del arr
            except Exception:
                pass
        cp.cuda.Stream.null.synchronize()
        gc.collect()
        cp.get_default_memory_pool().free_all_blocks()
        logging.info("Memória GPU liberada pelo context manager.")


def log_gpu_memory(stage: str) -> None:
    used = cp.get_default_memory_pool().used_bytes() / 1e6
    logging.info(f"[{stage}] Memória GPU usada: {used:.2f} MB")


# --- Logging Config ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audio_upscale")

# --- Type Aliases ---
NpArray: TypeAlias = np.ndarray
CpArray: TypeAlias = cp.ndarray


# --- Data Classes ---
@dataclass(frozen=True)
class AudioData:
    sample_rate: int
    samples: NpArray
    bitrate: Optional[int]
    audio_segment: AudioSegment


# --- I/O Handlers ---
def read_audio(file_path: str, fmt: str) -> AudioData:
    """
    Lê um arquivo de áudio e retorna metadados e amostras.
    Args:
        file_path: Caminho do arquivo.
        fmt: Formato do arquivo ('mp3', 'flac', 'ogg', 'wav').
    Returns:
        AudioData: Estrutura imutável com dados do áudio.
    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se o formato não for suportado.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    extra_params = ["-drc_scale", "0"]
    audio = AudioSegment.from_file(file_path, format=fmt, parameters=extra_params)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    sample_rate = audio.frame_rate

    # Pattern matching para bitrate
    match fmt:
        case "mp3":
            bitrate = MP3(file_path).info.bitrate
        case "flac":
            bitrate = FLAC(file_path).info.bitrate
        case "ogg":
            bitrate = OggVorbis(file_path).info.bitrate
        case "wav":
            bitrate = WAVE(file_path).info.bitrate
        case _:
            duration = len(audio) / 1000.0
            bitrate = int((len(samples) * 8) / duration) if duration > 0 else None

    # Ajuste para estéreo
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))

    return AudioData(
        sample_rate=sample_rate, samples=samples, bitrate=bitrate, audio_segment=audio
    )


def write_audio(file_path: str, sample_rate: int, data: NpArray, fmt: str) -> None:
    """
    Escreve dados de áudio em arquivo.
    Args:
        file_path: Caminho de saída.
        sample_rate: Taxa de amostragem.
        data: Amostras (NumPy).
        fmt: Formato de saída ('flac', 'wav').
    Raises:
        ValueError: Se o formato não for suportado.
    """
    match fmt:
        case "flac":
            sf.write(
                file_path,
                data.astype(np.float32),
                sample_rate,
                format="FLAC",
                subtype="PCM_32",
            )
        case "wav":
            sf.write(
                file_path,
                data.astype(np.float32),
                sample_rate,
                format="WAV",
                subtype="PCM_32",
            )
        case _:
            raise ValueError(f"Formato de saída não suportado: {fmt}")


# --- Processamento Funcional ---


def new_interpolation_algorithm(data: CpArray, upscale_factor: int) -> CpArray:
    """
    Interpola dados duplicando pontos via vetorização.
    Args:
        data: Sinal de entrada (CuPy).
        upscale_factor: Fator de upscaling.
    Returns:
        CpArray: Sinal expandido.
    """
    return cp.repeat(data, upscale_factor)


def initialize_ist(data: CpArray, threshold: float) -> CpArray:
    """
    Inicializa IST aplicando limiar.
    """
    return cp.where(cp.abs(data) > threshold, data, 0)


def iterative_soft_thresholding(
    data: CpArray, max_iter: int, threshold: float
) -> CpArray:
    """
    Aplica IST via FFT, com reconstrução harmônica.
    """
    data_thres = initialize_ist(data, threshold)
    for i in range(max_iter):
        # logger.info(f"iterative_soft_thresholding ({i})")
        data_fft = cp.fft.fft(data_thres)
        data_fft_thres = cp.where(cp.abs(data_fft) > threshold, data_fft, 0)
        data_thres = cp.fft.ifft(data_fft_thres).real
        harmonics = cp.sin(cp.linspace(0, 2 * cp.pi, len(data_thres)))
        data_thres += 0.1 * harmonics
    return data_thres


def lms_filter(
    signal: CpArray,
    desired: CpArray,
    mu: float = 0.001,
    num_taps: int = 32,
    block_size: int = 2048,
) -> CpArray:
    """
    Filtro LMS adaptativo vetorizado por blocos (Block LMS) usando CuPy.
    - Elimina locks, threads Python e overhead de sincronização.
    - Mantém a adaptação dos pesos entre blocos.
    - Totalmente funcional e imutável.
    """
    n: int = len(signal)
    w: CpArray = cp.zeros(num_taps, dtype=cp.float32)
    filtered_signal: CpArray = cp.zeros(n, dtype=cp.float32)
    num_blocks: int = (n - num_taps) // block_size

    for b in range(num_blocks):
        start: int = num_taps + b * block_size
        end: int = start + block_size
        # Monta matriz de blocos: cada linha é uma janela de num_taps
        X: CpArray = cp.stack(
            [signal[start - i : end - i] for i in range(num_taps)], axis=1
        )
        y: CpArray = X @ w
        e: CpArray = desired[start:end] - y
        # Atualiza pesos apenas uma vez por bloco
        w = w + 2 * mu / block_size * X.T @ e
        filtered_signal[start:end] = y
    return filtered_signal


def chunked_block_lms_filter(
    signal: CpArray,
    desired: CpArray,
    mu: float = 0.001,
    num_taps: int = 32,
    block_size: int = 2048,
    chunk_size: int = 10**6,
) -> CpArray:
    """
    Block LMS com chunking para sinais muito grandes.
    """
    n: int = len(signal)
    filtered_signal: CpArray = cp.zeros(n, dtype=cp.float32)
    w: CpArray = cp.zeros(num_taps, dtype=cp.float32)
    for chunk_start in range(0, n, chunk_size):
        chunk_end = min(chunk_start + chunk_size, n)
        filtered_signal[chunk_start:chunk_end] = lms_filter(
            signal[chunk_start:chunk_end],
            desired[chunk_start:chunk_end],
            mu=mu,
            num_taps=num_taps,
            block_size=block_size,
        )
        # Opcional: propague w se necessário (ajuste block_lms_filter para retornar w)
    return filtered_signal


def normalize_signal(signal: CpArray) -> CpArray:
    """
    Normaliza sinal para [-1, 1].
    Raises:
        ValueError: Se o sinal for vazio.
    """
    if signal.size == 0:
        raise ValueError("Sinal vazio não pode ser normalizado.")
    return signal / cp.max(cp.abs(signal))


def process_channel(
    channel: CpArray, upscale_factor: int, max_iter: int, threshold: float
) -> CpArray:
    """
    Pipeline funcional para um canal.
    """
    expanded = new_interpolation_algorithm(channel, upscale_factor)
    ist = iterative_soft_thresholding(expanded, max_iter, threshold)
    return expanded + ist


def upscale_channels(
    channels: CpArray, upscale_factor: int, max_iter: int, threshold: float
) -> CpArray:
    """
    Aplica pipeline funcional a todos os canais.
    """
    results = []
    for ch in channels.T:
        out = process_channel(ch, upscale_factor, max_iter, threshold)
        results.append(out)
        del ch, out
        cp.cuda.Stream.null.synchronize()
        cp.get_default_memory_pool().free_all_blocks()
        cp.fft.config.get_plan_cache().clear()
    return cp.column_stack(results)


# --- Pipeline Principal ---


@dataclass(frozen=True)
class UpscaleConfig:
    """
    Configuração imutável para o pipeline de upscaling de áudio.
    """

    input_file_path: str
    output_file_path: str
    source_format: str
    target_format: str = "flac"
    max_iterations: int = 300
    threshold_value: float = 0.6
    target_bitrate_kbps: int = 1411
    toggle_normalize: bool = True
    toggle_autoscale: bool = True
    toggle_adaptive_filter: bool = True


# --- Funções Utilitárias ---
def validate_config(cfg: UpscaleConfig) -> None:
    """
    Valida os parâmetros do pipeline.
    """
    valid_bitrate_ranges = {
        "flac": (800, 1411),
        "wav": (800, 6444),
    }
    if cfg.target_format not in valid_bitrate_ranges:
        raise ValueError(f"Formato de saída não suportado: {cfg.target_format}")
    min_bitrate, max_bitrate = valid_bitrate_ranges[cfg.target_format]
    if not (min_bitrate <= cfg.target_bitrate_kbps <= max_bitrate):
        raise ValueError(
            f"Bitrate {cfg.target_bitrate_kbps} fora do intervalo para {cfg.target_format}."
        )


def prepare_audio(cfg: UpscaleConfig) -> Tuple[CpArray, AudioData, int]:
    """
    Lê o áudio e calcula o fator de upscaling.
    """
    audio_data = read_audio(cfg.input_file_path, cfg.source_format)
    samples = cp.array(audio_data.samples, dtype=cp.float32)
    if audio_data.audio_segment.channels == 2:
        samples = samples.reshape((-1, 2))
    target_bitrate = cfg.target_bitrate_kbps * 1000
    upscale_factor = (
        round(target_bitrate / audio_data.bitrate) if audio_data.bitrate else 4
    )
    return samples, audio_data, upscale_factor


def process_channels(
    channels: CpArray, cfg: UpscaleConfig, upscale_factor: int
) -> CpArray:
    """
    Pipeline funcional: upscaling, autoscale, normalização, filtro adaptativo.
    """
    upscaled = upscale_channels(
        channels,
        upscale_factor=upscale_factor,
        max_iter=cfg.max_iterations,
        threshold=cfg.threshold_value,
    )
    if cfg.toggle_autoscale:
        upscaled = cp.column_stack(
            [
                normalize_signal(upscaled[:, i]) * cp.max(cp.abs(channels[:, i]))
                for i in range(channels.shape[1])
            ]
        )
    if cfg.toggle_normalize:
        upscaled = cp.column_stack(
            [normalize_signal(upscaled[:, i]) for i in range(upscaled.shape[1])]
        )
    if cfg.toggle_adaptive_filter:
        stak = [
            lms_filter(upscaled[:, i], upscaled[:, i]) for i in range(upscaled.shape[1])
        ]
        upscaled = cp.column_stack(stak)
    return upscaled


def write_output(
    cfg: UpscaleConfig, audio_data: AudioData, upscaled: CpArray, upscale_factor: int
) -> None:
    """
    Converte para NumPy e escreve o áudio processado no disco.
    """
    new_sample_rate = audio_data.sample_rate * upscale_factor
    final_audio = cp.asnumpy(upscaled)
    write_audio(
        cfg.output_file_path,
        new_sample_rate,
        final_audio,
        cfg.target_format,
    )
    del final_audio  # Libera RAM se necessário


# --- Função Principal Modularizada ---
def upscale(cfg: UpscaleConfig) -> None:
    """
    Pipeline principal de upscaling funcional de áudio, modular e seguro.
    """
    validate_config(cfg)
    logger.info(f"Lendo arquivo {cfg.input_file_path} ({cfg.source_format})...")
    samples, audio_data, upscale_factor = prepare_audio(cfg)
    logger.info(f"Fator de upscaling: {upscale_factor}")
    channels = samples[:, cp.newaxis] if samples.ndim == 1 else samples
    logger.info("Processando e upscaling dos canais...")
    with gpu_memory_scope(samples, channels):
        upscaled = process_channels(channels, cfg, upscale_factor)
        write_output(cfg, audio_data, upscaled, upscale_factor)
    logger.info("Arquivo salvo e memória GPU liberada.")
