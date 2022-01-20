import re
import time
from pathlib import Path
from typing import Dict, Optional

import nest_asyncio  # type: ignore # necessary import fix required for async to work in notebooks

from biolib import cli_utils
from biolib.biolib_logging import logger

nest_asyncio.apply()


class AppResult:
    def __init__(
        self,
        stdout: bytes,
        stderr: bytes,
        exitcode: int,
        files: Dict[str, bytes],
        main_output_file: Optional[str],
    ):
        self._stdout = stdout
        self._stderr = stderr
        self._exitcode = exitcode
        self._files = files
        self._main_output_file = main_output_file

    def __str__(self):
        return cli_utils.get_pretty_print_module_output_string(self._stdout, self._stderr, self._exitcode)

    def ipython_markdown(self):
        import IPython.display  # type:ignore # pylint: disable=import-error, import-outside-toplevel
        if self._main_output_file:
            if self._main_output_file not in self._files:
                logger.error("Error rendering output: main_output_file not found")
                markdown_str = ""
            else:
                markdown_str = self._files[self._main_output_file].decode('utf-8')
        else:
            markdown_str = self._stdout.decode('utf-8')
        # prepend ./biolib_results/ to all paths
        # ie [SeqLogo](./SeqLogo2.png) test ![SeqLogo](./SeqLogo.png)
        # ![SeqLogo](SeqLogo.png)  ![SeqLogo](/SeqLogo.png)
        # is transformed to ![SeqLogo](./biolib_results/SeqLogo2.png) test ![SeqLogo](./biolib_results/SeqLogo.png)
        # ![SeqLogo](./biolib_results/SeqLogo.png)  ![SeqLogo](./biolib_results/SeqLogo.png)
        markdown_str_modified = re.sub(
            r'\!\[([^\]]*)\]\((\.\/|\/|)([^\)]*)\)',
            r'![\1](./biolib_results/\3)',
            markdown_str,
        )
        IPython.display.display(IPython.display.Markdown(markdown_str_modified))

    def save_files(self, output_dir: str):
        logger.debug("Output Files:")

        for file_path, file_data in self._files.items():
            # Remove leading slash of file_path
            new_file_path = Path(output_dir) / Path(file_path.lstrip('/'))
            if new_file_path.exists():
                new_file_path.rename(f'{new_file_path}.biolib-renamed.{time.strftime("%Y%m%d%H%M%S")}')

            dir_path = new_file_path.parent
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)

            with open(new_file_path, 'wb') as output_file:
                output_file.write(file_data)
            logger.debug(f"  - {new_file_path}")

        logger.debug('\n')

    @property
    def stdout(self) -> bytes:
        return self._stdout

    @property
    def stderr(self) -> bytes:
        return self._stderr

    @property
    def exitcode(self) -> int:
        return self._exitcode
