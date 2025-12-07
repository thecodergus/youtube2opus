# main.py
from src.process_pipeline import process_youtube_links
from src.utils import clean_youtube_url

if __name__ == "__main__":
    # Exemplo de uso: forneça sua lista de links aqui
    youtube_links = [
        "https://www.youtube.com/watch?v=gA4GxTQtrKw",
        "https://www.youtube.com/watch?v=ETEg-SB01QY",
        "https://www.youtube.com/watch?v=w1nGMgaukcE",
        "https://www.youtube.com/watch?v=osPq9Yb8xm8",
        "https://www.youtube.com/watch?v=pcFK4HzAlsU",
        "https://www.youtube.com/watch?v=zMCVp6INpnw",
        "https://www.youtube.com/watch?v=3rkJ3L5Ce80",
        "https://www.youtube.com/watch?v=Ymwj0zcqnDw",
        "https://www.youtube.com/watch?v=C4gVlt46voo",
        "https://www.youtube.com/watch?v=k7xtF0axbjg",
        "https://www.youtube.com/watch?v=8pGbGjSD9kA",
        "https://www.youtube.com/watch?v=xLnhtTlwjak",
        "https://www.youtube.com/watch?v=L3vjm1gybU4",
        "https://www.youtube.com/watch?v=ysA7IeyfO3c",
        "https://www.youtube.com/watch?v=RRDQCuHYONg",
        "https://www.youtube.com/watch?v=mvA48_mEUMA",
        "https://www.youtube.com/watch?v=Nw1uB_ttKt8",
        "https://www.youtube.com/watch?v=YLJbYcX5LWk",
        "https://www.youtube.com/watch?v=0BNh7zpBoBU",
        "https://www.youtube.com/watch?v=nGMNLHufze4",
    ]
    youtube_links = list(map(clean_youtube_url, youtube_links))
    process_youtube_links(youtube_links, output_dir="./output")
