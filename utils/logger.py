# utils/logger.py
import logging
import os

def setup_logger(name):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        file_handler = logging.FileHandler(f"{log_dir}/{name}.log")
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s — %(name)s — %(levelname)s — %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
