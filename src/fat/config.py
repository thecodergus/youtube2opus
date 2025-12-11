from dataclasses import dataclass
from .types import AudioTypes


@dataclass(frozen=True)
class UpscaleConfig:
    input_file_path: str
    output_file_path: str
    source_format: AudioTypes
    target_format: AudioTypes
    max_iterations: int = 300
    threshold_value: float = 0.6
    target_bitrate_kbps: int = 1411
    toggle_normalize: bool = True
    toggle_autoscale: bool = True
    toggle_adaptive_filter: bool = True


def validate_config(cfg: UpscaleConfig) -> None:
    valid_bitrate_ranges = {
        AudioTypes.FLAC: (800, 1411),
        AudioTypes.WAV: (800, 6444),
    }
    if cfg.target_format not in valid_bitrate_ranges:
        raise ValueError(f"Formato de saída não suportado: {cfg.target_format}")
    min_bitrate, max_bitrate = valid_bitrate_ranges[cfg.target_format]
    if not (min_bitrate <= cfg.target_bitrate_kbps <= max_bitrate):
        raise ValueError(
            f"Bitrate {cfg.target_bitrate_kbps} fora do intervalo para {cfg.target_format}."
        )
