import os
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style
from loguru import logger
from rich.console import Console

from .fichub import FicHub
from .logging import download_processing_log, meta_fetched_log
from .processing import check_url

bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt}, {rate_fmt}{postfix}, ETA: {remaining}"
console = Console()


class FetchData:
    def __init__(self, out_dir="",
                 debug=False, automated=False, verbose=False):
        self.out_dir = out_dir
        self.debug = debug
        self.automated = automated
        self.exit_status = 0

    def get_metadata(self, _input: str):

        meta_list = []
        file_name = "metadata"
        supported_url = None

        # check if the input is a file
        if os.path.isfile(_input):
            if self.debug:
                logger.info(f"Input file: {_input}")
            # get the tail
            _, file_name = os.path.split(_input)
            file_name = os.path.splitext(file_name)[0]
            with open(_input, "r") as f:
                urls = f.read().splitlines()

        else:
            if self.debug:
                logger.info("Input is an URL")
            urls = [_input]

        with tqdm(total=len(urls), ascii=False,
                  unit="url", bar_format=bar_format) as pbar:

            for url in urls:
                download_processing_log(self.debug, url)
                pbar.update(1)
                supported_url, self.exit_status = check_url(
                    url, self.debug, self.exit_status)

                if supported_url:
                    fic = FicHub(self.debug, self.automated,
                                 self.exit_status)
                    fic.get_fic_extraMetadata(url)

                    if fic.fic_extraMetadata:
                        meta_list.append(fic.fic_extraMetadata)
                        meta_fetched_log(self.debug, url)

                        # update the exit status
                        self.exit_status = fic.exit_status
                    else:
                        self.exit_status = 1
                        supported_url = None

            meta_data = "{\"meta\": ["+", ".join(meta_list)+"]}"
            timestamp = datetime.now().strftime("%Y-%m-%d T%H%M%S")
            json_file = os.path.join(
                self.out_dir, file_name) + f" - {timestamp}.json"

            if meta_list:
                with open(json_file, "w") as outfile:
                    if self.debug:
                        logger.info(f"Saving \"{json_file}\"")
                    outfile.write(meta_data)

                tqdm.write(Fore.GREEN +
                           "\nMetadata saved as " + Fore.BLUE +
                           f"{os.path.abspath(json_file)}"+Style.RESET_ALL +
                           Style.RESET_ALL)
