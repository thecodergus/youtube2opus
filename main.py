# main.py
from src.process_pipeline import process_youtube_links
from src.utils import clean_youtube_url

if __name__ == "__main__":
    # Exemplo de uso: forneça sua lista de links aqui
    youtube_links = [
        "https://www.youtube.com/watch?v=m8QQR-wQA0I&list=RDm8QQR-wQA0I&start_radio=1&pp=ygUOc3RhcnQgc2hvcHBpbmegBwE%3D",
    ]
    youtube_links = list(map(clean_youtube_url, youtube_links))
    process_youtube_links(youtube_links, output_dir="./output")
