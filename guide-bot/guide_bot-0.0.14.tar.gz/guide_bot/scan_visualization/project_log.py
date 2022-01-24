import os
import yaml

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from guide_bot.logging.log_plotter import LogPlotter

class ProjectLog:
    def __init__(self, project_path):
        self.project_path = project_path
        overview_path = os.path.join(project_path, "run_overview.yaml")

        with open(overview_path, 'r') as ymlfile:
            self.overview = yaml.safe_load(ymlfile)

        self.guides = self.overview["guide_names"]

        self.log_files = {}
        self.log_files_loaded = {}
        for guide in self.guides:
            self.log_files[guide] = []
            self.log_files_loaded[guide] = {}

    def find_all_log_files(self):
        for guide in self.guides:
            foldername = os.path.join(self.project_path, guide)
            for file in os.listdir(foldername):
                if file.endswith(".log"):
                    file_path = os.path.join(self.project_path, guide, file)
                    self.log_files[guide].append(file_path)

            self.log_files[guide].sort()

    def load_log_plotter(self, guide_name, filename):
        if filename not in self.log_files[guide_name]:
            raise KeyError("This file should not exist?")

        if filename not in self.log_files_loaded[guide_name]:
            log_plotter = LogPlotter(filename)
            self.log_files_loaded[guide_name][filename] = log_plotter
        else:
            log_plotter = self.log_files_loaded[guide_name][filename]

        return log_plotter

    def plot_fom_guide_ax(self, ax, guide_name, cs_start=0, cs_end=1, **kwargs):
        colors = cm.rainbow(np.linspace(cs_start, cs_end, len(self.log_files[guide_name])))
        for log_file, color in zip(self.log_files[guide_name], colors):
            log_plotter = self.load_log_plotter(guide_name, log_file)
            log_plotter.plot_1D_fom_ax(ax, color=color, **kwargs)

    def plot_fom_all_ax(self, ax, **kwargs):
        n_guides = len(self.guides)
        cs_start = [x/n_guides for x in range(n_guides)]
        cs_end = [(x+1)/n_guides for x in range(n_guides)]

        for guide, cs_start, cs_end in zip(self.guides, cs_start, cs_end):
            self.plot_fom_guide_ax(ax, guide, cs_start, cs_end, **kwargs)

    def plot_fom_all(self, figsize=(12, 10)):

        fig, ax = plt.subplots(figsize=figsize)

        self.plot_fom_all_ax(ax)

        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
        plt.show()

    def plot_fom_each(self, figsize=(12, 8)):

        for guide in self.guides:
            if len(self.log_files[guide]) == 0:
                print("No guides from " + str(guide) + " yet.")
                continue

            fig, ax = plt.subplots(figsize=figsize)

            self.plot_fom_guide_ax(ax, guide)

            # Shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            # Put a legend to the right of the current axis
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.show()

    def plot_overview_logfile(self, logfile):
        Found = False
        for guide_name in self.log_files:
            logfile_names = [os.path.split(logfile)[1] for logfile in self.log_files[guide_name]]
            if logfile in logfile_names:
                logfile_index = logfile_names.index(logfile)
                logfile = self.log_files[guide_name][logfile_index]
                Found = True
                break

        if not Found:
            raise KeyError("Did not find this log file")

        print(logfile)
        log_plotter = self.load_log_plotter(guide_name, logfile)
        log_plotter.plot_overview()

    def plot_overviews_guide(self, guide_name):
        for log_file in self.log_files[guide_name]:
            log_plotter = self.load_log_plotter(guide_name, log_file)
            log_plotter.plot_overview()

    def plot_all_overviews(self):
        for guide in self.guides:
            self.plot_overviews_guide(guide)






