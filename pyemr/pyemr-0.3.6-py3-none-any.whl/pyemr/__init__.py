# pylint: disable=R0201,C0413
"""Command Line Interface"""
import os
from pprint import pprint
from subprocess import check_output

from pkg_resources import get_distribution

from pyemr.utils.build import build
from pyemr.utils.config import init_pyemr
from pyemr.utils.docker import launch_docker_bash, launch_docker_shell
from pyemr.utils.emr import (
    cancel_step, describe_cluster, describe_step, get_clusters_list_df,
    get_step_state, list_steps, ssm_cluster,
)
from pyemr.utils.export import export_airflow_template
from pyemr.utils.linting import format_code, lint_wd, spell_check
from pyemr.utils.logs import (
    download_all_emr_logs, print_application_id, print_emr_log_files_lines,
    print_emr_log_path, summarize_logs,
)
from pyemr.utils.mocking import mock_part_s3_folder, mock_s3_folder
from pyemr.utils.notebook import (
    install_mock_python_kernel, launch_mock_notebook_docker,
    run_notebook_in_poetry, run_notebook_on_sys,
)
from pyemr.utils.python import (
    launch_mock_python_docker, launch_mock_python_sys, launch_mock_python_venv,
)
from pyemr.utils.submit import submit_spark_step
from pyemr.utils.sys import os_cmd
from pyemr.utils.testing import (
    test_script_with_s3_mock_docker, test_script_with_s3_mock_sys,
    test_script_with_s3_mock_venv,
)


# Its standard to have a version parameter in the module __init__.py.
__version__ = get_distribution("pyemr").version


class Cli:
    """PYEMR:
        Command line toolkit for pyspark on EMR.

    Args:

    Returns:

    """

    def init(
        self,
        project_name="",
        target_cluster="",
        s3_stage_dir="",
        stage="",
        region="",
    ):
        """Create a pyproject.toml containing pyemr config.

        Args:
          project_name: str : Name of your python package. (Default value = "")
          target_cluster: str: Name of EMR cluster to run your package on. (Default value = "")
          s3_stage_dir: str: s3 location for storing project code, project build and other artifacts. (Default value = "")
          stage: str : The run stage, either dev, qa or prod. (Default value = "")
          region: str: The s3 emr region. (Default value = "")

        Returns:

        """
        init_pyemr(project_name, target_cluster, s3_stage_dir, stage, region)

    def ssh(self, cluster_name="default"):
        """A proxy name for ssm.

        Args:
          cluster_name: Name of the emr clusters. (Default value = "default")

        Returns:

        """
        self.ssm(cluster_name)

    def ssm(self, cluster_name="default"):
        """smm into the cluster master node.

        Args:
          cluster_name: (Default value = "")

        Returns:

        """
        ssm_cluster(cluster_name)

    def build(self):
        """Zips the python package and its dependencies, then uploads them s3 staging directory."""
        build()

    def cluster_submit(self, script, *args, **kwargs):
        """Submit the script with the package dependencies in cluster mode.

        Args:
          script: Path to python script.
          *args: Script arguments.
          **kwargs: Script arguments.
          cluster_name: name of the cluster to submit to.

        Returns:

        """
        self.submit(script, *args, **kwargs, submit_mode="cluster", wait=True)

    def submit(
        self,
        script,
        *args,
        **kwargs,
    ):
        """Submit the script with the package dependencies (default = cleint mode).

        Args:
          script: Path to python script.
          *args: Script arguments.
          **kwargs: Script arguments.
          cluster_name: name of the cluster to submit to.
          submit_mode: Either 'client' or 'cluster'
          wait: bool: wait for the job of run it asynchronously.

        Returns:

        """
        cluster_name = kwargs.pop("cluster_name", "")
        submit_mode = kwargs.pop("submit_mode", "client")
        wait = kwargs.pop("wait", True)

        submit_spark_step(
            local_script_path=script,
            submit_mode=submit_mode,
            cluster_name=cluster_name,
            wait=wait,
            script_args=args,
            script_kwargs=kwargs,
        )

    def config(self):
        """Open the project config file."""
        input_dir = os.getcwd()
        check_output(["open", f"{input_dir}/pyproject.toml"])

    def export(
        self,
        local_script_path,
        *args,
        **kwargs,
    ):
        """Export step as airflow dag.

        Args:
          self:
          local_script_path:
          submit_mode: Spark submit mode, either 'client' or 'cluster'
          action_on_failure: (Default value = 'CONTINUE')
          *args:
          **kwargs:

        Returns:

        """
        submit_mode = kwargs.pop("submit_mode", "cluster")
        action_on_failure = kwargs.pop("action_on_failure", "CONTINUE")

        # assert type in ["aws", "bash", "python", "airflow", "awswrangler"]
        export_airflow_template(
            local_script_path,
            submit_mode=submit_mode,
            action_on_failure=action_on_failure,
            args=args,
            kwargs=kwargs,
        )

    def steps(
        self,
        cluster_name="default",
        n=10,
        step_name="{env_name}:*",
        states="*",
        all=False,
    ):
        """List steps on cluster.

        Args:
          cluster_name: (Default value = "")
          n: (Default value = 10)
          step_name: (Default value = "*{env_name}*")
          states: (Default value = '*')
          all: (Default value = False)

        Returns:

        """
        if all:
            step_name = states = "*"
        pprint(list_steps(cluster_name, n, step_name, states, print_info=True))

    def cancel(
        self,
        step_id="latest",
        cluster_name="default",
        step_name_pattern="{env_name}:*",
        state="*",
    ):
        """Cancel a spark step (defaults to last step).

        Args:
          step_id: (Default value = "")
          cluster_name: (Default value = "")
          step_name_pattern: (Default value = "*{env_name}*")
          state: (Default value = "*")

        Returns:

        """
        pprint(cancel_step(cluster_name, step_id, step_name_pattern, state))

    def describe_step(
        self,
        step_id="latest",
        cluster_name="default",
        name="{env_name}:*",
        state="*",
    ):
        """Describe a step (defaults to last step).

        Args:
          step_id: (Default value = "")
          cluster_name: (Default value = "")
          name: (Default value = "*{env_name}*")
          state: (Default value = "*")

        Returns:

        """
        pprint(describe_step(cluster_name, step_id, name, state))

    def stderr(
        self,
        step_id="latest",
        n=30,
        cluster_name="default",
        name="*{env_name}*",
        state="*",
        out_dir="logs",
    ):
        """Print last n lines of spark step (defaults to last step).

        Args:
          step_id: Step id to get stderr out (Default value = "")
          n: Number of lines to print (Default value = 30)
          cluster_name: Name of cluster to find step (Defaults to config cluster.)
          name: Pattern to filter step name (Default value = "*{env_name}*")
          state: The step state (Default value = "*")
          out_dir: Output to save logs. (Default value = "./logs")

        Returns:

        """
        print_emr_log_files_lines(
            "stderr",
            n,
            step_id,
            cluster_name,
            name,
            state,
            out_dir,
            "FAIL",
        )

    def stdout(
        self,
        step_id="latest",
        n=30,
        cluster_name="default",
        name="*{env_name}*",
        state="*",
        out_dir="logs",
    ):
        """Get step stdout (defaults to last step).

        Args:
          step_id: Step id to get stdout for (Default value = "")
          n: Number of lines to print (Default value = 30)
          cluster_name: Name of cluster to find step (Defaults to config cluster.)
          name: Pattern to filter step name (Default value = "*{env_name}*")
          state: The step state (Default value = "*")
          out_dir: Output to save logs. (Default value = "./logs")

        Returns:

        """
        print_emr_log_files_lines(
            "stdout",
            n,
            step_id,
            cluster_name,
            name,
            state,
            out_dir,
            "OKCYAN",
        )

    def state(
        self,
        step_id="latest",
        cluster_name="default",
        name="*{env_name}*",
        state="*",
    ):
        """Get state of last step.

        Args:
          step_id: Step id to check for (Defaults to last step.)
          cluster_name: Name of cluster to find step (Defaults to config cluster_name.)
          name: Pattern to filter step name (Default value = "*{env_name}*")
          state: The step state (Default value = "*")

        Returns:

        """
        get_step_state(cluster_name, step_id, name, state)

    def describe_cluster(self, cluster_name="default"):
        """

        Args:
          cluster_name: (Default value = "")

        Returns:

        """
        pprint(describe_cluster(cluster_name))

    def clusters(self, states="RUNNING|WAITING", n=10):
        """List the clusters in the given states.

        Args:
          states: (Default value = "RUNNING|WAITING" )
          n: (Default value = 10)

        Returns:

        """
        print(get_clusters_list_df(states, n))

    def notebook(self, env: str = "docker", additional_site_package_paths: str = ""):
        """Launch a jupyter notebooks with s3 patch.

        Args:
          env: str: The environment to run the notebook in.
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")

        Returns:

        """
        assert env in ["sys", "local", "os", "poetry", "venv", "docker", "linux"]

        if env in ["sys", "local", "os"]:
            run_notebook_on_sys()

        if env in ["venv", "poetry"]:
            run_notebook_in_poetry()

        if env in ["docker", "linux"]:
            launch_mock_notebook_docker()

    def venv_python(self, additional_site_package_paths: str = ""):
        """Launches interactive python session with s3 patch inside the virtual env.

        Args:
          additional_site_package_paths: str:  (Default value = '')
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")
          additional_site_package_paths: str:  (Default value = "")

        Returns:

        """
        launch_mock_python_venv()

    def python(self, env: str = "docker", additional_site_package_paths: str = ""):
        """Runs interactive docker python session with s3 patch.

        Args:
          env: str: The environment to run the python session in (sys|venv|docker)
          env: str:  (Default value = "docker")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")
          env: str:  (Default value = "docker")
          additional_site_package_paths: str:  (Default value = "")

        Returns:

        """
        assert env in ["sys", "local", "os", "poetry", "venv", "docker", "linux"]

        if env in ["sys", "local", "os"]:
            launch_mock_python_sys()

        if env in ["poetry", "venv"]:
            launch_mock_python_venv()

        if env in ["docker", "linux"]:
            launch_mock_python_docker()

    def sh(self):
        """Stats a docker shell session."""
        launch_docker_shell()

    def bash(self):
        """Stats a docker bash session."""
        launch_docker_bash()

    def local_test(self, script, *args, **kwargs):
        """Run a script locally with s3 patch.

        Args:
          script: path to python script
          *args: script arguments
          **kwargs: script arguments

        Returns:

        """
        test_script_with_s3_mock_venv(script, *args, **kwargs)

    def test(self, script, *args, **kwargs):
        """Run a script inside the docker container with s3 patch.

        Args:
          script: path to python script
          *args: script arguments
          **kwargs: script arguments
          env: (Default value = 'docker')

        Returns:

        """
        env = kwargs.pop("env", "docker")
        kwargs.pop("additional_site_package_paths", "")

        assert env in ["sys", "local", "os", "poetry", "venv", "docker", "linux"]

        if env in ["sys", "local", "os"]:
            test_script_with_s3_mock_sys(script, args, kwargs)

        if env in ["poetry", "venv"]:
            test_script_with_s3_mock_venv(script, args, kwargs)

        if env in ["docker", "linux"]:
            test_script_with_s3_mock_docker(script, args, kwargs)

    def linux_test(self, script, *args, **kwargs):
        """Run a script inside the docker linux container with s3 patch.

        Args:
          script:
          *args:
          **kwargs:

        Returns:

        """
        test_script_with_s3_mock_docker(script, *args, **kwargs)

    def vtest(self, script, *args, **kwargs):
        """Run a script inside the virtual enviroment linux container with s3 patch.

        Args:
          script:
          *args:
          **kwargs:

        Returns:

        """
        test_script_with_s3_mock_venv(script, *args, **kwargs)

    def logs(
        self,
        step_id="latest",
        cluster_name="default",
        name="*{env_name}*",
        state="*",
        out_dir="logs",
    ):
        """Downloads logs for a step, and creates a summary or errors/warnings.

        Args:
          out_dir: (Default value = "logs")
          step_id: (Default value = "")
          cluster_name: (Default value = "")
          name: (Default value = "*{env_name}*")
          state: (Default value = "*")

        Returns:

        """
        download_all_emr_logs(cluster_name, step_id, name, state, out_dir)
        summarize_logs(cluster_name, step_id, name, state, out_dir)

    def local(self, script, *args, **kwargs):
        """Test locally. Outside the docker, but with s3 mocking.

        Args:
          script:
          *args:
          **kwargs:

        Returns:

        """
        self.local_test(script, *args, **kwargs)

    def lint(self, *args, **kwargs):
        """Lints the code in the current directory.

        Args:
          *args: Arguments to be pasted to pylint.
          **kwargs: Arguments to be pasted to pylint.

        Returns:

        """

        lint_wd(*args, **kwargs)

    def format(self):
        """Auto-formats the code in the current directory."""
        format_code()

    def mock(self, s3_path: str, all: bool = False):
        """Finds and downloads a part of an s3 table/directory the file.

        Args:
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)
          s3_path: str:
          all: bool:  (Default value = False)

        Returns:

        """

        if all:
            mock_s3_folder(s3_path)
        else:
            mock_part_s3_folder(s3_path)

    def spellcheck(self, path):
        """Spell check a path.

        Args:
          path:

        Returns:

        """
        spell_check(path)

    def add(self, *args, **kwargs):
        """Adds required packages to your pyproject.toml and installs it in the venv.

        Args:
          *args: Arguments to pass to 'poetry add'.
          **kwargs: Arguments to pass to 'poetry add'.

        Returns:

        """
        os_cmd("poetry", "add", *args, **kwargs)

    def logs_url(
        self,
        step_id="latest",
        cluster_name="default",
        name="*{env_name}*",
        state="*",
    ):
        """Print s3 log url for last step

        Args:
          step_id: (Default value = "latest")
          cluster_name: (Default value = "default")
          name: (Default value = "*{env_name}*")
          state: (Default value = "*")

        Returns:

        """
        print_emr_log_path(
            cluster_name,
            step_id,
            name,
            state,
        )

    def app_id(
        self,
        step_id="latest",
        cluster_name="default",
        name="*{env_name}*",
        state="*",
        out_dir="logs",
    ):
        """Prints application id for a step (defaults to last submitted step)

        Args:
          step_id: (Default value = "latest")
          cluster_name: (Default value = "default")
          name: (Default value = "*{env_name}*")
          state: (Default value = "*")
          out_dir: (Default value = "logs")

        Returns:

        """
        print_application_id(cluster_name, step_id, name, state, out_dir)

    def install_pyemr_kernel(self):
        """ """
        install_mock_python_kernel()
        print("Done.")
