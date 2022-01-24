import os
import subprocess


class BaseJob:
    job_name: str

    custom_start_block: int

    start_block: int

    end_block: int

    workspace_dir: str

    def __init__(self,
                 job_name: str,
                 custom_start_block: int,
                 end_block: int,
                 workspace_dir: str):

        self.job_name = job_name
        self.start_block_custom = custom_start_block
        self.start_block = custom_start_block
        self.end_block = end_block

        if workspace_dir is not None:
            self.workspace_dir = workspace_dir

        start_block_cache = self.get_next_start()
        if start_block_cache != 0:
            self.start_block = start_block_cache

    def get_conf_file_name(self):
        return f'{self.job_name}_{self.start_block_custom}_{self.end_block}_conf'

    def get_conf_file_path(self):
        return f'{self.workspace_dir}/{self.get_conf_file_name()}'

    def save_next_start(self, next_start: int):
        conf_file_path = self.get_conf_file_path()
        with open(conf_file_path, 'w+') as f:
            f.write(str(next_start))

    def get_next_start(self) -> int:
        conf_file_path = self.get_conf_file_path()

        if not os.path.isfile(conf_file_path):
            return 0

        with open(conf_file_path, 'r') as f:
            content = f.read()
            if len(content) == 0:
                return 0
            else:
                return int(content)

    @staticmethod
    def system_call_with_output(command: [str]) -> (str, bool):
        try:
            output = subprocess.run(command, check=True, capture_output=True).stdout.decode()
            success = True
        except subprocess.CalledProcessError as e:
            output = e.output.decode()
            success = False
        return output, success
