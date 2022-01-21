from colorama import Fore
from loguru import logger
from tqdm import tqdm


def download_processing_log(debug: bool, url: str):
    if debug:
        logger.info(f"Processing {url.strip()}")
    else:
        tqdm.write(Fore.BLUE + f"\nProcessing {url.strip()}")


def meta_fetched_log(debug: bool, url: str):
    if debug:
        logger.info(f"Metadata fetched for {url}")
    else:
        tqdm.write(Fore.GREEN + f"Metadata fetched for {url}")
