# main.py
from src.process_pipeline import process_youtube_links
from src.utils import clean_youtube_url

if __name__ == "__main__":
    # Exemplo de uso: forneça sua lista de links aqui
    youtube_links = [
        "https://www.youtube.com/watch?v=OxYLMplSGwo",
        "https://www.youtube.com/watch?v=mpZrpOY7ABo",
        "https://www.youtube.com/watch?v=YxUoWqfedKc",
        "https://www.youtube.com/watch?v=vT5tC-qZ3lI",
        "https://www.youtube.com/watch?v=s3vdNNBX98w",
        "https://www.youtube.com/watch?v=fLko2bFrwLA",
        "https://www.youtube.com/watch?v=rngLO3tF2mA",
        "https://www.youtube.com/watch?v=oT0cJl3SnMo",
        "https://www.youtube.com/watch?v=KtHULOEGUpY",
        "https://www.youtube.com/watch?v=wmR3REi27ZQ",
        "https://www.youtube.com/watch?v=NvRUpkTrTGk",
        "https://www.youtube.com/watch?v=E7sP6t1QyrI",
        "https://www.youtube.com/watch?v=bpOSxM0rNPM",
        "https://www.youtube.com/watch?v=V0r0CLhm23M",
        "https://www.youtube.com/watch?v=SlCXgj2bS_A",
    ]
    youtube_links = list(map(clean_youtube_url, youtube_links))
    process_youtube_links(youtube_links, output_dir="./output")
