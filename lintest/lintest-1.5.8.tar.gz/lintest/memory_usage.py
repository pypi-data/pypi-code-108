# this module is used to log the memory usage
# @author: Wang Lin

# import time
# import psutil
# import os
# from . import get_project_info
#
# project_info = get_project_info.get_project_info()


def log_memory_usage(status_desc, testcase=None):
    # 暂时不开启
    return

    # memory_usage_log_file_path = project_info.output_folder + os.sep + "memory_usage.log"
    #
    # with open(memory_usage_log_file_path, "a") as memory_usage_log:
    #     current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    #     memory_usage_log.write("Time: " + current_time + " |  Memory Usage: " +
    #                            str(psutil.virtual_memory()) + " | CPU Usage: " + str(psutil.cpu_percent()) + "%s" % (" | Testcase: " + str(testcase).split(" ")[0] if
    #                                                                   testcase is not None else "") + " | In Status(%s)" % status_desc + os.linesep)


if __name__ == "__main__":
    log_memory_usage()
