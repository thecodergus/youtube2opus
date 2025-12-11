import cupy as cp
from .config import UpscaleConfig, validate_config
from .logging_config import logger
from .gpu_utils import gpu_memory_scope
from .io_handlers import read_audio, write_audio
from .processing import (
    upscale_channels,
    normalize_signal,
    lms_filter,
)


def prepare_audio(cfg: UpscaleConfig):
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
    channels: cp.ndarray, cfg: UpscaleConfig, upscale_factor: int
) -> cp.ndarray:
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
    cfg: UpscaleConfig, audio_data, upscaled: cp.ndarray, upscale_factor: int
) -> None:
    new_sample_rate = audio_data.sample_rate * upscale_factor
    final_audio = cp.asnumpy(upscaled)
    write_audio(
        cfg.output_file_path,
        new_sample_rate,
        final_audio,
        cfg.target_format,
    )
    del final_audio


def upscale(cfg: UpscaleConfig) -> None:
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
