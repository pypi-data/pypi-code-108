import time as t
import numpy as np
import matplotlib.pyplot as plt

MINOR_TRESHOLD = 5

class TimeAnalyzer():

    def __init__(self):
        
        self.last_time = t.time()
        self.checkpoints = {}
        self.times = []
        self.count = []
        
        self.time_log = []
        

    def track(self, name, log = False):
        """
        Track the time elapsed between either
        * the creation time of the TimeAnalyzer, or
        * the last time this method was called
        and the point in time when this method is called.

        :param name: Name the measured elapsed time should be associated with
        :type name: str

        :param log: ?, defaults to False
        :type log: bool
        """
        time = t.time()
        if log:
            self.time_log.append((name, time))
        else:
            current_time = time - self.last_time
            self.last_time = time
            if name in self.checkpoints:
                name_id = self.checkpoints[name]
                self.times[name_id] += current_time
                self.count[name_id] += 1
            else:
                new_id = len(self.checkpoints)
                self.checkpoints[name] = new_id
                self.times.append(current_time)
                self.count.append(1)
            
    def get_times(self):
        return list(self.checkpoints), self.times, self.count
    
    def get_log(self):
        return self.time_log
    
    def save_times(self, file_name = 'time', graphical = False, drop_minors = True):
        relatives = np.zeros(len(self.times))
        names = list(self.checkpoints)

        with open(file_name + '.ta', 'w') as f:
            f.write("Name Time Counter Time/Count\n")
            for i, (name, time, c) in enumerate(zip(names, self.times, self.count)):
                r = time/c
                relatives[i] = r
                f.write(name + " " + str(time) + " " + str(c) + " " + str(float(r)) + "\n")

        ordered_relatives = sorted(relatives)
        ordered_relatives_names = [x for _,x in sorted(zip(relatives, names))]
        ordered_count = [x for _,x in sorted(zip(relatives, self.count))]

        if drop_minors:
            removal = []
            for i, (c, r, n) in enumerate(zip(ordered_count, ordered_relatives, ordered_relatives_names)):
                if c < MINOR_TRESHOLD:
                    removal.append([r,n])

            for r,n in removal:
                ordered_relatives.remove(r)
                ordered_relatives_names.remove(n)

        ordered_times = sorted(self.times)
        ordered_names = [x for _,x in sorted(zip(self.times, names))]

        if graphical:
            plt.figure()
            plt.bar(names, relatives)
            plt.xticks(rotation = 90)
            plt.savefig(file_name + "_time_analysis_relative.png",bbox_inches='tight')
            plt.close()

            plt.figure()
            plt.bar(names, self.times)
            plt.xticks(rotation=90)
            plt.savefig(file_name + '_time_analysis.png',bbox_inches='tight')
            plt.close()

            plt.figure()
            plt.bar(ordered_relatives_names, ordered_relatives)
            plt.xticks(rotation=90)
            plt.savefig(file_name + "_time_analysis_ordered_relative.png",bbox_inches='tight')
            plt.close()

            plt.figure()
            plt.bar(ordered_names, ordered_times)
            plt.xticks(rotation=90)
            plt.savefig(file_name + "_time_analysis_ordered.png",bbox_inches='tight')
            plt.close()


    def save_log(self, file_name = 'time'):
        with open(file_name + '.log', 'w') as f:
            for name, time in self.time_log:
                f.write(name + " " + str(time) + "\n")
