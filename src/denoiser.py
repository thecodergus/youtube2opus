# src/denoiser.py
from df.enhance import enhance, init_df, load_audio, save_audio


def denoise_wav(input_wav: str, output_wav: str) -> None:
    """
    Aplica denoising ao arquivo WAV usando DeepFilterNet (df).
    """
    model, df_state, _ = init_df()
    audio, _ = load_audio(input_wav, sr=df_state.sr())
    enhanced = enhance(model, df_state, audio)
    save_audio(output_wav, enhanced, df_state.sr())
