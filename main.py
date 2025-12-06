# main.py
from src.types import DownloadConfig, AudioFormat, UrlList
from src.utils import ensure_directory_exists
from src.downloader import download_audio


def main(
    youtube_links: UrlList, output_dir: str, audio_format: AudioFormat = AudioFormat.M4A
) -> None:
    """
    Orquestra o fluxo de validação, configuração e download.
    """
    ensure_directory_exists(output_dir)
    config = DownloadConfig(
        output_dir=output_dir,
        audio_format=audio_format,
    )
    download_audio(youtube_links, config)


if __name__ == "__main__":
    youtube_links: UrlList = [
        "https://www.youtube.com/watch?v=YLJbYcX5LWk",
        "https://www.youtube.com/watch?v=Nw1uB_ttKt8",
    ]
    output_path: str = "./output"
    main(youtube_links, output_path, audio_format=AudioFormat.MP3)
