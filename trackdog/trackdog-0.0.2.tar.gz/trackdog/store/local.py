import logging
import os
import uuid
import csv

from trackdog.store.util import ensure_dir, ensure_file
from trackdog.model import Project, Run, Metric

metric_format_suffix = ".csv"

# TODO(gaocegege): Make a base class to support other stores.
class LocalStore():
    def __init__(self, root=None):
        self.logger = logging.getLogger(__name__)
        if root is None:
            self.base_path = os.path.expanduser("~/.trackdog")
        else:
            self.base_path = root

    @property
    def project(self):
        return self._project.name

    @property
    def run(self):
        return self._run.name

    @classmethod
    def get_project(cls, project_name):
        if project_name is None:
            return Project(uuid.uuid4().hex)
        return Project(project_name)

    @classmethod
    def get_run(cls, project_name, run_name):
        if run_name is None:
            return Run(uuid.uuid4().hex, project_name)
        return Run(run_name, project_name)

    def init(self, project_name=None, run_name=None):
        self._project = LocalStore.get_project(project_name)
        self._run = LocalStore.get_run(project_name, run_name)
        self._run_path = os.path.join(self.base_path, self.project, self.run)
        ensure_dir(self._run_path)
        self.handles = {}

    # TODO(gaocegege): Use column format to save data.
    def track(self, val, name, epoch=None, step=None):
        self.logger.debug('storing metric %s for project %s, run %s',
                          name, self.project, self.run)
        f_name = os.path.join(self._run_path, "{}{}".format(name, metric_format_suffix))
        if name not in self.handles:
            ensure_file(f_name)
            handle = open(f_name, "w")
            self.handles[name] = csv.writer(handle)
        self.handles[name].writerow([val, epoch, step])

    def get_projects(self, project_name=None):
        if project_name is None:
            projects = []
            for name in os.listdir(self.base_path):
                project = Project(name)
                for run_name in os.listdir(os.path.join(self.base_path, name)):
                    project.add_run(run_name)
                projects = projects + [project]
        else:
            project = Project(project_name)
            for run_name in os.listdir(os.path.join(self.base_path, project_name)):
                project.add_run(run_name)
            projects = [project]
        return projects

    def get_runs(self, project_name=None, run_name=None):
        if project_name is None:
            projects = os.listdir(self.base_path)
        else:
            projects = [project_name]

        if run_name is None:
            runs = []
            for project in projects:
                run_names = os.listdir(os.path.join(self.base_path, project))
                for name in run_names:
                    run = Run(name, project)
                    for f in os.listdir(os.path.join(self.base_path, project, name)):
                        if f.endswith(metric_format_suffix):
                            run.add_metric(f[:-4])
                    runs.append(run)
        else:
            for project in projects:
                if run_name in os.listdir(os.path.join(self.base_path, project)):
                    project_name = project
            run = Run(run_name, project_name)
            for f in os.listdir(os.path.join(self.base_path, project_name, run_name)):
                if f.endswith(metric_format_suffix):
                    run.add_metric(f[:-4])
            runs = [run]
        return runs

    def get_metric(self, project_name, run_name, metric_name):
        metric = Metric(metric_name, project_name, run_name)
        with open(os.path.join(self.base_path, project_name,
        run_name, "{}.csv".format(metric_name)), "r") as f:
            reader = csv.reader(f)
            for row in reader:
                # TODO(gaocegege): Make it more efficeint.
                metric.add_datapoint(float(row[0]))
        return metric
