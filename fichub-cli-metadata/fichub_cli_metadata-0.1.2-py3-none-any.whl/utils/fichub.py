import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from colorama import Fore, Style
from tqdm import tqdm
from loguru import logger
import json
import time

headers = {
    'User-Agent': 'fichub_cli_metadata/0.1.2',
}

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)


class FicHub:
    def __init__(self, debug, automated, exit_status):
        self.debug = debug
        self.automated = automated
        self.exit_status = exit_status
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

    def get_fic_extraMetadata(self, url: str):

        params = {'q': url}
        if self.automated:  # for internal testing
            params['automated'] = 'true'
            if self.debug:
                logger.debug(
                    "--automated flag was passed. Internal Testing mode is on.")

        for _ in range(2):
            try:
                response = self.http.get(
                    "https://fichub.net/api/v0/epub", params=params,
                    allow_redirects=True, headers=headers, timeout=(6.1, 300)
                )
                if self.debug:
                    logger.debug(
                        f"GET: {response.status_code}: {response.url}")
                break
            except (ConnectionError, TimeoutError, Exception) as e:
                if self.debug:
                    logger.error(str(e))
                tqdm.write("\n" + Fore.RED + str(e) + Style.RESET_ALL +
                           Fore.GREEN + "\nWill retry in 3s!" +
                           Style.RESET_ALL)
                time.sleep(3)

        try:
            self.response = response.json()
            self.fic_extraMetadata = json.dumps(
                self.response['meta'], indent=4)

        # if metadata not found
        except (KeyError, UnboundLocalError) as e:
            if self.debug:
                logger.error(str(e))

            with open("err.log", "a") as file:
                file.write(url.strip()+"\n")

            self.exit_status = 1
            self.fic_extraMetadata = ""
            tqdm.write(
                Fore.RED + f"\nSkipping unsupported URL: {url}" +
                Style.RESET_ALL + Fore.CYAN +
                "\nTo see the supported site list, use " + Fore.YELLOW +
                "fichub_cli -ss" + Style.RESET_ALL + Fore.CYAN +
                "\nReport the error if the URL is supported!\n")
