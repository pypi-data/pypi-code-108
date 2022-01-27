import os
import socket
import datetime
import traceback

try:
    import lintest
except ImportError:
    traceback.print_exc()


def convert_to_seconds(t):
    try:
        s_time = str(t)
        # print("start to covert to seconds:" + s_time)
        if "." in s_time:
            s_time, ms = s_time.split(".")
            ms = "0." + ms
        else:
            ms = 0
        h, m, s = s_time.split(":")
        h, m, s = int(h), int(m), int(s)
        s_time = h * 3600 + m * 60 + s + float(ms)
        s_time = str(s_time)
        return s_time
    except BaseException:
        traceback.print_exc()
        return t


def generate_xunit_result(passed_testcases, failed_testcases, output_folder, begin_time):
    end_time = datetime.datetime.now()
    execution_time = end_time - begin_time

    with open(output_folder + os.sep + "xunitresults.xml", "w", encoding='utf-8') as xml_file:
        pass_count = len(passed_testcases)
        fail_count = len(failed_testcases)

        xml_file.write(
            "<testsuite failures='%s' tests='%s' name='Automation Run' hostname='%s' time='%s' timestamp='%s' type='lintest_%s'>\n" % (
                fail_count, pass_count + fail_count, socket.getfqdn(), execution_time, begin_time,
                lintest.__version__))

        for failed_testcase in failed_testcases:
            xml_file.write("    <testcase classname='%s' name='%s' time='%s' status='fail'>\n" % (
                failed_testcase.__module__, failed_testcase.__class__.__name__,
                failed_testcase.execution_time))

            # the value of xml's attribute must not contains the "<" or ">" character, here replace "<" to "&lt;" and
            # replace ">" to "&gt;" and replace "&" to "&amp;" and replace " to '
            xml_file.write(
                "        <failure message=\"%s\">\n" % failed_testcase.exception_info_for_xml_report.replace('"',
                                                                                                             "'").replace(
                    "<", "&lt;").replace(">", "&gt;").replace("&", "&amp;"))

            xml_file.write(
                failed_testcase.traceback_info.replace('"', "'").replace("<", "&lt;").replace(">", "&gt;").replace("&",
                                                                                                                   "&amp;"))
            xml_file.write("        </failure>\n")

            xml_file.write("        <system-out>\n")

            with open(failed_testcase.logfile_full_name, "r", encoding='utf-8') as f:
                full_log = f.read()
                xml_file.write(
                    full_log.replace('"', "'").replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;"))

            xml_file.write("        </system-out>\n")

            xml_file.write("    </testcase>\n\n")

        for passed_testcase in passed_testcases:
            xml_file.write("    <testcase classname='%s' name='%s' time='%s' status='pass'>\n" % (
                passed_testcase.__module__, passed_testcase.__class__.__name__,
                passed_testcase.execution_time))

            xml_file.write("        <system-out>\n")
            with open(passed_testcase.logfile_full_name, "r", encoding='utf-8') as f:
                full_log = f.read()
                xml_file.write(
                    full_log.replace('"', "'").replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;"))

            xml_file.write("        </system-out>\n")
            xml_file.write("    </testcase>\n\n")

        xml_file.write("</testsuite>")
