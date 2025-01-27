import logging


def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(f"evo.{name}")
