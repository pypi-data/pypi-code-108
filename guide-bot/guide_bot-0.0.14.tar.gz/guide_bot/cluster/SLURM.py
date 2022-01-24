import os
import yaml
import platform

from guide_bot.cluster.Base import ClusterBase


class ClusterSLURM(ClusterBase):
    def __init__(self, cluster_name, config_path=None):
        """
        Class for writing files for SLURM clusters

        Parameters
        ----------
        cluster_name: str
            Name of cluster and base of configuration filename

        config_path: str
            Path to config files, if None use cluster_config folder
        """

        self.cluster_name = cluster_name
        self.filename = cluster_name + ".yaml"

        super().__init__(config_path)

        self.queue_info = None
        self.address = None

    def _write_configuration(self):
        """
        Writes a dummy configuration file
        """

        current_setup_lines = ["source /etc/profile.d/modules.sh",
                                "module avail",
                                "module purge",
                                "module load mcstas/2.7",
                                "module load gcc/10.2.0",
                                "module load openmpi/4.0_gcc1020",
                                "module list",
                                "which mcrun",
                                "source ../../../venv/bin/activate"]

        long = {"maxhours": 24,
                "n_cores": 12,
                "python_exe": "python3",
                "setup_lines": current_setup_lines}

        newlong = {"maxhours": 24,
                   "n_cores": 24,
                   "python_exe": "python3",
                   "setup_lines": current_setup_lines}

        DMSC = {"Address": "login.esss.dk", "queues": {"long": long, "newlong": newlong}}

        with open(self.filename, 'w') as yaml_file:
            yaml.dump(DMSC, yaml_file, default_flow_style=False)

    def read_configuration(self):
        """
        Reads the configuration file and saves information in attributes
        """

        config_file = os.path.join(self.config_path, self.filename)
        with open(config_file, 'r') as ymlfile:
            read_data = yaml.safe_load(ymlfile)

        self.queue_info = read_data["queues"]
        self.address = read_data["Address"]

        for queue in self.queue_info:
            self.queue_info[queue]["launch_file"] = os.path.join(self.project_path, "launch_all_" + str(queue) + ".sh")

    def start_launch_script(self):
        """
        Writes the start of the launch script for each queue

        The launch script will launch all the optimization batch files, the
        file is started before any calls to write_task are made. Still need
        to make the script executable with chmod +X.
        """

        for queue in self.queue_info:
            with open(self.queue_info[queue]["launch_file"], "w") as file:
                file.write("#!/bin/bash\n")

            if platform.system() == "Linux" or platform.system() == "Darwin":
                os.system("chmod +x " + self.queue_info[queue]["launch_file"])

    def write_task(self, foldername, scan_name):
        """
        Writes batch files for all queues and adds to respective launch files

        The write_task method will generate batch files for running an
        optimization using each available queue on the cluster, and add a call
        to this batch file to the appropriate launch_all script. In this way
        the user can select which queue to run on after the project is
        generated.

        Parameters
        ----------
        foldername: str
            Name of the folder in which to run files

        scan_name: str
            scan name of this guide optimization, name of plk file
        """

        for queue in self.queue_info:
            batch_file = self.generate_run_batch(scan_name, queue, nodes=1)

            with open(self.queue_info[queue]["launch_file"], "a") as file:
                file.write("cd " + foldername + "\n")
                file.write("sbatch " + batch_file + "\n")
                file.write("cd ..\n")

    def generate_run_batch(self, scan_name, queue, maxhours=None, nodes=1):
        """
        Method for writing batch file for SLURM cluster

        Uses information in configration file to write a batch file that will
        perform a guide optimization using the stored task file in plk format.

        Parameters
        ----------
        scan_name: str
            Name of the folder in which to run files

        queue: str
            Name of queue (must be in configuration data)

        maxhours: int
            Maximum number of hours to run this job

        nodes
            Number of nodes to use
        """

        if queue not in self.queue_info:
            raise KeyError("The selected queue wasn't found in loaded configuration.")

        queue_info = self.queue_info[queue]

        nodes = int(nodes)  # Checks nodes is an integer

        n_cores = queue_info["n_cores"] * nodes

        # compare selected time to time limit
        time_limit = queue_info["maxhours"]
        if maxhours is not None:
            time_limit = min(maxhours, time_limit)

        filename = scan_name + "_" + queue + ".batch"

        f = open(filename, "w")

        f.write("#!/bin/bash\n")
        f.write("#SBATCH --job-name=" + str(scan_name) + "\n")
        err_name = "err_" + scan_name + "_" + str(queue) + ".stderr\n"
        f.write("#SBATCH --error=" + err_name)
        out_name = "out_" + scan_name + "_" + str(queue) + ".stdout\n"
        f.write("#SBATCH --output=" + out_name + "\n")
        f.write("#SBATCH --nodes " + str(nodes) + "\n")
        f.write("#SBATCH --partition=" + str(queue) + "\n")
        f.write("#SBATCH --time=" + str(time_limit-1) + ":59:00\n")
        f.write("#SBATCH --exclusive\n")
        f.write("\n")
        f.write("\n")
        for setup_line in queue_info["setup_lines"]:
            f.write(setup_line + "\n")

        f.write("\n")
        python_bin = queue_info["python_bin"]

        statement1 = "from guide_bot.logic import runner"
        statement2 = "runner.RunFromFile('" + scan_name + ".plk', settings={'mpi':" + str(n_cores) + "})"

        f.write(python_bin + " -c \"" + statement1 + ";" + statement2 + "\"\n")

        f.write("\n")
        f.write("scontrol show jobid=$SLURM_JOB_ID >> NLjob1_run.env.slurm.txt\n")
        f.close()

        return filename

