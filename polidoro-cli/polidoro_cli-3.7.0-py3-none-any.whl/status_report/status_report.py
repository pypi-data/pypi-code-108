# import os
# import sys
# from ctypes import c_char
# from io import StringIO
# from multiprocessing import Process, Manager, Value, Array
# from subprocess import Popen, PIPE
# from time import sleep
#
#
# class StatusStdOut(StringIO):
#     def __init__(self, stdout):
#         self.stdout = stdout
#
#     def write(self, s):
#         self.stdout += s
#
#
# class StatusStruct(object):
#     def __init__(self, process):
#         self.status = ""
#         self.process = process
#
#
# class StatusProcess(Process):
#     def __init__(self, *args, **kwargs):
#         self.stdout = Manager().list("")
#         kwargs["kwargs"]["stdout"] = self.stdout
#         super(StatusProcess, self).__init__(*args, **kwargs)
#
#     def __str__(self):
#         return "".join(self.stdout)
#
# LIMPAR_ATE_O_FIM_DA_LINHA = '\x1b[K'
# class StatusReport(object):
#     processes = {}
#
#     @staticmethod
#     def run(name, cmd, *args, **kwargs):
#         # sys.stdout = StatusStdOut()
#         #         try:
#         #             while p.poll() is None:
#         #                 if verbose and p.stdout is not None:
#         #                     print(p.stdout.readline().decode(), end="")
#         #                     print(p.stderr.readline().decode(), end="")
#         p = StatusProcess(target=StatusReport._parallel_run, args=(cmd,) + args, kwargs=kwargs)
#         p.start()
#         StatusReport.processes[name] = p
#         while p.is_alive():
#             # os.system("clear")
#             info = str(p).split("\n")[-6:]
#             if info:
#                 # print(info)
#                 for i in info:
#                     print(i)
#                     os.system("tput el")
#                 os.system("tput cuu %d" % len(info))
#             sleep(0.1)
#         p.join()
#         # sys.stdout = sys.__stdout__
#
#     @staticmethod
#     def _parallel_run(cmd, *args, verbose=True, folder=None, stdout=None, **kwargs):
#         sys.stdout = StatusStdOut(stdout)
#         if folder:
#             os.chdir(folder)
#         try:
#             if isinstance(cmd, str):
#                 p = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
#                 while p.poll():
#                     if verbose:
#                         print(p.stdout.readline().decode(), end="")
#                         print(p.stderr.readline().decode(), end="")
#                 if verbose:
#                     line = p.stdout.readline()
#                     while line:
#                         print(line.decode(), end="")
#                         line = p.stdout.readline()
#                     # [print(l.decode(), end="") for l in p.stdout.readlines()]
#                     # [print(l.decode(), end="") for l in p.stderr.readlines()]
#
#                 return p.poll()
#             if callable(cmd):
#                 print("call")
#
#         except KeyboardInterrupt:
#             pass
#         finally:
#             sys.stdout = sys.__stdout__
#
#     @staticmethod
#     def print_report():
#         pass
