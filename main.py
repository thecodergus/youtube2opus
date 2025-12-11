# main.py
from src.process_pipeline import process_youtube_links
from src.utils import clean_youtube_url

if __name__ == "__main__":
    # Exemplo de uso: forneça sua lista de links aqui
    youtube_links = [
        # "https://www.youtube.com/watch?v=m8QQR-wQA0I",
        # "https://www.youtube.com/watch?v=b4PWTnXKVhE",
        # "https://www.youtube.com/watch?v=F2kTxddHeZs",
        # "https://www.youtube.com/watch?v=voGfr0LeCYk",
        # "https://www.youtube.com/watch?v=BjJlBiHYUak",
        # "https://www.youtube.com/watch?v=Hjs0mArKmrE",
        # "https://www.youtube.com/watch?v=Z9PM5gjwN1U",
        # "https://www.youtube.com/watch?v=Nw1uB_ttKt8",
        # "https://www.youtube.com/watch?v=Cy44ocuoWhE",
        # "https://www.youtube.com/watch?v=YLJbYcX5LWk",
        # "https://www.youtube.com/watch?v=ZMHgW1CDono",
        # "https://www.youtube.com/watch?v=75P0QGi3RO0",
        # "https://www.youtube.com/watch?v=VkeLkuFzPfM",
        # "https://www.youtube.com/watch?v=nGMNLHufze4",
        # "https://www.youtube.com/watch?v=x_artPecEaM",
        # "https://www.youtube.com/watch?v=ysA7IeyfO3c",
        "https://www.youtube.com/watch?v=gA4GxTQtrKw&list=RDgA4GxTQtrKw&start_radio=1&pp=oAcB"
    ]
    youtube_links = list(map(clean_youtube_url, youtube_links))
    process_youtube_links(youtube_links, output_dir="./output")
