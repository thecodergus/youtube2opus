# file_utils.py
import os


def ensure_directory_exists(path: str) -> None:
    """
    Garante que o diretório existe, criando-o se necessário.
    """
    os.makedirs(path, exist_ok=True)
