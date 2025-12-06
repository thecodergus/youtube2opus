# denoiser.py
from typing import Final
from df.enhance import enhance, init_df, load_audio, save_audio


def denoise_wav(input_wav: str, output_wav: str) -> None:
    """
    Aplica denoising ao arquivo WAV usando DeepFilterNet (df) conforme documentação oficial.
    Função pura, imutável e auditável.
    """
    model, df_state, _ = init_df()  # Carrega modelo padrão (DeepFilterNet2)
    audio, _ = load_audio(input_wav, sr=df_state.sr())
    enhanced = enhance(model, df_state, audio)
    save_audio(output_wav, enhanced, df_state.sr())
