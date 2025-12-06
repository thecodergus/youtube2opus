# main.py
from src.process_pipeline import process_youtube_links


if __name__ == "__main__":
    # Exemplo de uso: forneça sua lista de links aqui
    youtube_links = [
        "https://www.youtube.com/watch?v=m8QQR-wQA0I",
    ]
    process_youtube_links(youtube_links, output_dir="./output")
