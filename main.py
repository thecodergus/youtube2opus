# main.py
from src.process_pipeline import process_youtube_links
from src.utils import clean_youtube_url

if __name__ == "__main__":
    # Exemplo de uso: forneça sua lista de links aqui
    youtube_links = [
        "https://www.youtube.com/watch?v=b4PWTnXKVhE&list=RDEMqpK9LGA9e6RUqfcXCJBXeQ&start_radio=1",
        # "https://www.youtube.com/watch?v=F2kTxddHeZs&list=RDEMqpK9LGA9e6RUqfcXCJBXeQ&index=2",
        # "https://www.youtube.com/watch?v=voGfr0LeCYk&list=RDEMqpK9LGA9e6RUqfcXCJBXeQ&index=6",
        # "https://www.youtube.com/watch?v=BjJlBiHYUak&list=RDEMqpK9LGA9e6RUqfcXCJBXeQ&index=7",
        # "https://www.youtube.com/watch?v=Hjs0mArKmrE&list=RDEMqpK9LGA9e6RUqfcXCJBXeQ&index=9",
    ]
    youtube_links = list(map(clean_youtube_url, youtube_links))
    process_youtube_links(youtube_links, output_dir="./output")
