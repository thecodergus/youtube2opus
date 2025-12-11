import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("audio_upscale")


logger = setup_logging()
