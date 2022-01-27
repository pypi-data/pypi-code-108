import os
import shutil

import pandas as pd
from reprox import core, submit_jobs, process_job, validate_run
from bson import json_util
import unittest
import strax
import json
import subprocess
import glob


class TestingHacks:
    @staticmethod
    def hack_squeue():
        def _return_dali(*args, **kwargs):
            return 'dali'

        submit_jobs.cycle_queue = _return_dali

    @staticmethod
    def hack_njobs():
        def _return_zero():
            return 0

        submit_jobs.n_jobs_running = _return_zero

    @staticmethod
    def hack_execute_command():
        def _fake_submit(*args, **kwargs):
            cmd = kwargs['jobstring']
            # disable bandit
            result = subprocess.run(cmd, shell=True, capture_output=True)  # noqa
            core.log.info(f'{cmd} gave \n {result}')

        process_job.ProcessingJob._submit = _fake_submit

    @staticmethod
    def hack_changing_user_group():
        def _do_nothing(*args, **kwargs):
            pass

        validate_run.change_ownership = _do_nothing

    def perform_testing_hacks(self):
        self.hack_squeue()
        self.hack_njobs()
        self.hack_execute_command()


class TestSubmitJobs(unittest.TestCase, TestingHacks):
    context = 'xenonnt_online'
    package = 'straxen'
    target = 'event_info_double'
    dummy_md = os.path.join(os.path.abspath('.'), '.dummy_md.json')
    runs = tuple(f'{r:06}' for r in range(20_000, 20_050))
    dest_folder = os.path.join(core.config['context']['base_folder'], 'strax_data')

    def setUp(self) -> None:
        self.write_csv()
        self.write_dummy_json(self.dummy_md, {'chunks': [{'n': 0}]})
        st = self.get_context()

        keys = [st.key_for('run_id', t) for t in strax.to_str_tuple(self.target)]

        # Hack new command format
        command = """
cd {base_folder}
echo \
    {run_name} \
    --target {target} \
    --context {context} \
    --package {package} \
    --timeout {timeout} 
    {extra_options}
"""

        for k in keys:
            data_dir = self.dest_folder + '/{run_name}' + f'-{k.data_type}-{k.lineage_hash}'
            command += f'\nmkdir -p {data_dir}'
            command += f'\ncp {self.dummy_md} {data_dir}/{k.data_type}-{k.lineage_hash}-metadata.json'
        command += "\necho Processing job ended"
        core.command = command
        self.perform_testing_hacks()

    def tearDown(self) -> None:
        if os.path.exists(self.dummy_md):
            os.remove(self.dummy_md)
        for folder in glob.glob(os.path.join(self.dest_folder, '*')):
            shutil.rmtree(folder)

    def test_submit_jobs(self):
        self.write_test_log()
        submit_jobs.submit_jobs(clear_logs=True)

    @staticmethod
    def write_test_log():
        with open(core.log_fn.format(run_id='test'), 'a') as file:
            file.write('Test')

    def test_move_all(self):
        submit_jobs.submit_jobs()
        validate_run.move_all()

    def get_context(self):
        return core.get_context(context=self.context, package=self.package)

    def write_csv(self):
        runs = pd.DataFrame({'name': self.runs,
                             'number': [int(r) for r in self.runs]
                             })
        pd.DataFrame(runs).to_csv(core.runs_csv)

    def write_dummy_json(self, path: str, content: dict) -> None:
        folder = os.path.split(path)[0]
        os.makedirs(folder, exist_ok=True)

        with open(path, mode='w') as f:
            f.write(json.dumps(content, default=json_util.default))
