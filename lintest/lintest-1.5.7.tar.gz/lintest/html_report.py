"""
1. generate the automation test html report
2. can filter test cases by tag/package

@author: Wang Lin
"""
import os
import datetime
import traceback
import lintest
import collections


try:
    import settings
except BaseException:
    traceback.print_exc()
    raise BaseException("there are no settings/__init__.py found in your project ...")

from .ui_testcase import UITestCase
from .xml_report import convert_to_seconds


# used to map all the test cases
def map_testcases_package(all_testcases_package, testcase_map_tag, testcase_filter_tag, testcase):
    if "." not in testcase_filter_tag:
        testcase.testcase_filter_tag += testcase_filter_tag
        testcase.testcase_filter_tag += "~"
        all_testcases_package.add(testcase_filter_tag)
        testcase_map_tag[testcase_filter_tag].append(testcase)
    else:
        all_testcases_package.add(testcase_filter_tag)
        if testcase_filter_tag in testcase_map_tag.keys():
            testcase_map_tag[testcase_filter_tag].append(testcase)
            testcase.testcase_filter_tag += testcase_filter_tag
            testcase.testcase_filter_tag += "~"
        else:
            testcase_map_tag[testcase_filter_tag] = []
            testcase_map_tag[testcase_filter_tag].append(testcase)
            testcase.testcase_filter_tag += testcase_filter_tag
            testcase.testcase_filter_tag += "~"

        testcase_filter_tag = testcase_filter_tag[0:testcase_filter_tag.rfind(".")]
        map_testcases_package(all_testcases_package, testcase_map_tag, testcase_filter_tag, testcase)


class Reporter(object):

    def __init__(self, output_folder, passed_cases, failed_cases, error_cases, start_time, platform_info, auto_refresh):
        try:
            self.generate_html_report(output_folder, passed_cases, failed_cases, error_cases, start_time,
                                      platform_info, auto_refresh)
        except BaseException:
            traceback.print_exc()

    def generate_html_report(self, output_folder, passed_cases, failed_cases, error_cases, start_time, platform_info,
                             auto_refresh):
        with open(output_folder + os.sep + "report.html", "w") as report_file_handler:
            back_ground_color_page = "#FFFFFF"
            bg_color_column = "#ADADAD"
            end_time = datetime.datetime.now()
            execution_time = end_time - start_time
            execution_time = convert_to_seconds(execution_time)

            failed_cases_count = len(failed_cases)
            if failed_cases_count > 1:
                if settings.RERUN_FLAG:
                    failed_cases_count = failed_cases_count / 2

            failed_cases_count = int(failed_cases_count)

            css = """
            <style type="text/css">
                a:link,a:visited{
                    text-decoration:none;
                }
                a:hover{
                    text-decoration:underline;
                    background-color:#8E8E8E;
                }
            </style>
            """

            # java script code for filter function
            java_script_code_for_filter = """
            <script type="text/javascript">

                function changeTag(){
                    var my_select = document.getElementById("testcase_tag");
                    if (my_select.value == "tests"){
                        //all_failed_test_cases is  represent for all failed test cases
                        if(document.getElementById("all_failed_test_cases")){
                            all_failed_test_case = document.getElementById("all_failed_test_cases");
                            all_failed_test_case.style.display="none";
                            all_failed_test_case.style.display="block";

                            all_failed_case_list = document.getElementsByClassName("all_failed_case");
                            for(var i=0;i<all_failed_case_list.length;i++){
                                all_failed_case_list[i].style.display="block";
                            }
                            document.getElementById("num_fail").innerHTML=i;
                        }

                        //all_passed_test_cases is  represent for all passed test cases
                        if (document.getElementById("all_passed_test_cases")){
                            all_passed_test_case = document.getElementById("all_passed_test_cases");
                            all_passed_test_case.style.display="none";
                            all_passed_test_case.style.display="block";
                            all_passed_case_list = document.getElementsByClassName("all_passed_case");

                            for(var j=0;j<all_passed_case_list.length;j++){
                                all_passed_case_list[j].style.display="block";
                            }
                            document.getElementById("num_pass").innerHTML=j;
                        }
                    }

                    var l = new Array()
                    k = 0;
                    all_failed_case_list = document.getElementsByClassName("all_failed_case");

                    for(var i=0;i<all_failed_case_list.length;i++){
                        all_failed_case_list[i].style.display="none";

                        if (all_failed_case_list[i].getAttribute("name").indexOf(my_select.value) != -1){
                            l[k] = all_failed_case_list[i];
                            k = k + 1;
                        }
                    }

                    all_passed_case_list = document.getElementsByClassName("all_passed_case");

                    for(var i=0;i<all_passed_case_list.length;i++){
                        all_passed_case_list[i].style.display="none";
                        if (all_passed_case_list[i].getAttribute("name").indexOf(my_select.value) != -1){
                            l[k] = all_passed_case_list[i];
                            k = k + 1;
                        }
                    }

                    if (document.getElementById("all_failed_test_cases")){
                        all_failed_test_case = document.getElementById("all_failed_test_cases");
                        all_failed_test_case.style.display="none";
                        all_failed_test_case.style.display="block";
                    }

                    if (document.getElementById("all_passed_test_cases")){
                        all_passed_test_case = document.getElementById("all_passed_test_cases");
                        all_passed_test_case.style.display="none";
                        all_passed_test_case.style.display="block";
                    }

                    num_failed_case = 0;
                    num_passed_case = 0;

                    for(var i=0;i<l.length;i++){
                        l[i].style.display="block";
                        if ("all_failed_case"==l[i].className){
                            num_failed_case = num_failed_case + 1;
                        }
                        if ("all_passed_case"==l[i].className){
                            num_passed_case = num_passed_case + 1;
                        }
                    }

                    if (document.getElementById("num_fail")){
                        document.getElementById("num_fail").innerHTML=num_failed_case;
                    }
                    if (document.getElementById("num_pass")){
                        document.getElementById("num_pass").innerHTML=num_passed_case;
                    }
                }

            </script>
            """

            java_script_copy_failed_testcases = """
            <script>
                function copyFailedTestCase(){
                    document.getElementById("failed_testcase_names").style.display="none";
                    if (%s === 1){
                        document.getElementById("copy_status_info").innerHTML = "<font color=darkgoldenrod>Copied 1 TestCase</font>";
                    } else if(%s > 1){
                        document.getElementById("copy_status_info").innerHTML = "<font color=darkgoldenrod>Copied %s TestCases</font>";
                    }
                    setTimeout(function(){
                        document.getElementById("copy_status_info").innerHTML = "";
                        document.getElementById("failed_testcase_names").style.display="block";
                    }, 2000);
                }
            </script>
            """ % (len(failed_cases), len(failed_cases), failed_cases_count)

            # refresh_string = "<meta http-equiv=\"Refresh\" content=\"60\" />"

            js_code_str = """
            <html>
                <head>
                    <title>Automation Test Report</title>
                    %s
                    %s
                    %s
                </head>
                <script type="text/javascript" src="https://cdn.jsdelivr.net/clipboard.js/1.5.12/clipboard.min.js"></script>
                <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5.0.2/dist/echarts.min.js"></script>
            """ % (
                css,
                java_script_code_for_filter,
                java_script_copy_failed_testcases
            )

            report_file_handler.write(js_code_str)

            environment = settings.ENVIRONMENT

            str_top_table = """
            <body  bgcolor='%s'>
            <table align='center' cellpadding=0 cellspacing=0 style='border-collapse: collapse' width='925'>
                <tr>
                    <td>
                        <div id='chart_div' style="min-width: 500px; height: 300px; margin: 0 auto"></div>
                    </td>
                    <td>
                        <table border='1' align='center' cellpadding=3 cellspacing=3 style='border-collapse: collapse' width='425'>
                            <tr  bgcolor='%s'>
                                <td>
                                    <font color='#2850A5'>&nbsp; Report Generate Time</font>
                                </td>
                                <td width='180' align='center'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'> &nbsp; Total Execution Time</font>
                                </td>
                                <td width='150' align='center'><font color='#2850A5'>%s (Seconds)</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'>  &nbsp; Total Test Cases</font>
                                </td>
                                <td align='center' width='150'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'>  &nbsp; Passed</font>
                                </td>
                                <td align='center'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'>  &nbsp; Failed</font>
                                </td>
                                <td align='center'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'>  &nbsp; Environment</font>
                                </td>
                                <td align='center'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'>  &nbsp; Threads Count</font>
                                </td>
                                <td align='center'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'>  &nbsp; Execution Host</font>
                                </td>
                                <td align='center'>
                                    <font color='#2850A5'>%s</font>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <font color='#2850A5'> &nbsp; Test Framework</font>
                                </td>
                                <td align='center'>
                                    <font color='#2850A5'>lintest==%s</font>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            <br>
            """ % (
                back_ground_color_page,
                bg_color_column,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %p"),
                execution_time,
                len(passed_cases) + failed_cases_count,
                len(passed_cases),
                failed_cases_count,
                environment,
                settings.QUEUE_SIZE,
                platform_info,
                lintest.__version__
            )

            report_file_handler.write(str_top_table)

            all_testcases = passed_cases + failed_cases
            all_testcases_package = set()
            if len(all_testcases) > 0:
                all_testcases_package = set()
                tc_map_tag = dict()
                tc_map_tag["tests"] = []

                # begin to fetch all the testcase's tags(according to the testcase' package)
                for testcase in all_testcases:
                    testcase.testcase_filter_tag = "~"
                    testcase_filter_tag = testcase.__module__[0:testcase.__module__.rfind(".")]
                    map_testcases_package(all_testcases_package, tc_map_tag, testcase_filter_tag, testcase)

            # generate the drop down list for all the different tags
            html_drop_down_list = """
            <table border='0' align='center' cellpadding=0 cellspacing=0 style='border-collapse: collapse' width='925'>
                <tr>
                    <td width='200'>Filter Test Cases By Package: </td>
                    <td>
            """
            report_file_handler.write(html_drop_down_list)

            all_testcases_package_list = []
            for testcase in all_testcases_package:
                all_testcases_package_list.append(testcase)

            all_testcases_package_list.sort()
            report_file_handler.write("<select id=\"testcase_tag\" onchange=\"changeTag()\">")
            for testcase in all_testcases_package_list:
                report_file_handler.write("<option value='%s'>" % testcase)
                report_file_handler.write("%s" % testcase)
                report_file_handler.write("</option>")
            report_file_handler.write("</select>")
            report_file_handler.write("</td><td align='left'><p id='copy_status_info'></p></td><td>")

            if len(failed_cases) > 0:
                str_failed_testcase_names = ""

                for failed_testcase in failed_cases:
                    str_failed_testcase_names += failed_testcase.__class__.__name__ + " "

                str_failed_testcases = """
                <div align="center" color="darkgoldenrod">
                    <button id="failed_testcase_names" class='failed_testcase_names' data-clipboard-text="%s" onclick="copyFailedTestCase()">
                        <font color='darkgoldenrod'>Click to Copy the Failed TestCase Names!</font>
                    </button>
                </div>
                <script>
                    new Clipboard('.failed_testcase_names');
                </script>
                """ % str_failed_testcase_names

                report_file_handler.write(str_failed_testcases)

            report_file_handler.write("</td></tr></table>")
            report_file_handler.write("<br>")

            if len(failed_cases) > 0:
                failed_testcase_table = """
                <table border='1' align='center' cellpadding=3 cellspacing=3 style='border-collapse: collapse' width='925'>
                    <tr id='all_failed_test_cases' bgcolor='%s' width='925'>
                        <td width='125' align='center'>
                            <b>
                                <font color='#A52812'>TestCaseID</font>
                            </b>
                        </td>
                        <td width='650' style='word-break:break-all' align='center'>
                            <b>
                                <font id='num_fail' color='#A52812'>%s Test %s Failed</font>
                            </b>
                        </td>
                        <td width='150' align='center'>
                            <b>
                                <font color='#A52812'>Execution Time</font>
                            </b>
                        </td>
                    </tr>
                """ % (
                    bg_color_column,
                    failed_cases_count,
                    "Cases" if failed_cases_count > 1 else "Case"
                )

                report_file_handler.write(failed_testcase_table)

                sorted_failed_cases = []

                if settings.RERUN_FLAG:
                    failed_cases_dict = {}
                    for tc in failed_cases:
                        module_name = tc.__module__.replace(".", "_") + os.sep + tc.__class__.__name__
                        if tc.rerun_tag == 1:
                            module_name = module_name + "_rerun"
                        failed_cases_dict[module_name] = tc
                    od = collections.OrderedDict(sorted(failed_cases_dict.items()))
                    for k in od.keys():
                        sorted_failed_cases.append(od[k])
                else:
                    sorted_failed_cases = failed_cases

                for failed_testcase in sorted_failed_cases:
                    module_name = failed_testcase.__module__.replace(".", "_") + os.sep + failed_testcase.__class__.__name__
                    module_name_display = failed_testcase.__module__.replace("tests.", "&#x0009;")
                    module_name_display += os.sep + failed_testcase.__class__.__name__
                    report_file_handler.write(
                        "<tr class='all_failed_case' name=%s  width='925'>" % failed_testcase.testcase_filter_tag)

                    report_file_handler.write(
                        "<td width='125' align='center' style='word-break:break-all;no-wrap:no-wrap'>")
                    report_file_handler.write(
                        "<a title='Click to go to test center' href='https://testcenter.lintest.com/testlink/linkto.php?tprojectPrefix=ET&item=testcase&id=ET-%s'><font color='#A52812'>" % getattr(
                            failed_testcase, "testcase_id", "None"))
                    report_file_handler.write("%s" % getattr(failed_testcase, "testcase_id", "None"))
                    report_file_handler.write("</font></a>")
                    report_file_handler.write("</td>")

                    testcase_information = """
                        <td width='650'style='word-break:break-all'>
                        <a  href='%s'>
                            <font color='#2850A5'>
                                %s
                            </font>
                        </a>
                        """ % (
                        module_name,
                        module_name_display
                    )

                    report_file_handler.write(testcase_information)

                    try:
                        report_file_handler.write(
                            " <a title='%s'> (" % 'Please see the execution logs for more details' + failed_testcase.exception_info + ") </a>")
                    except BaseException:
                        print(traceback.format_exc())

                    if failed_testcase.rerun_tag == 0:
                        try:
                            report_file_handler.write(
                                "<a title='Log' href='%s'>        <font color='#F18428'>   Log</font> </a>" %
                                failed_testcase.log_file_path)
                        except BaseException:
                            print(traceback.format_exc())

                        try:
                            if isinstance(failed_testcase, UITestCase):
                                report_file_handler.write(
                                    "<a title='Screenshot' href='%s'> <font color='#F18428'> - Screenshot</font> </a>" %
                                    failed_testcase.screenshot)
                        except BaseException:
                            print(traceback.format_exc())

                    elif failed_testcase.rerun_tag == 1:
                        try:
                            report_file_handler.write(
                                "<a title='ReRun_Log' href='%s'> <font color='#F18428'> | ReRun_Log</font> </a>" %
                                failed_testcase.log_file_path)
                        except BaseException:
                            print(traceback.format_exc())

                        try:
                            if isinstance(failed_testcase, UITestCase):
                                report_file_handler.write(
                                    "<a title='ReRun_Screenshot' href='%s'> <font color='#F18428'> - ReRun_Screenshot</font> </a>" %
                                    failed_testcase.rerun_screenshot)
                        except BaseException:
                            print(traceback.format_exc())

                    report_file_handler.write("</td>")

                    report_file_handler.write("<td width='150' align='center' >")
                    report_file_handler.write("<font color='#A52812'>")
                    if not hasattr(failed_testcase, "execution_time"):
                        failed_testcase.execution_time = ""
                    report_file_handler.write("%s" % failed_testcase.execution_time)
                    report_file_handler.write("</font>")
                    report_file_handler.write("</td></tr>")
                report_file_handler.write("</table>")
            report_file_handler.write("<br>")

            if len(passed_cases) > 0:
                passed_testcase_table = """
                <table border='1' align='center' cellpadding=3 cellspacing=3 style='border-collapse: collapse' width='925'>
                    <tr id='all_passed_test_cases' bgcolor='%s' width='925'>
                        <td width='125' align='center'>
                            <b>
                                <font color='#2850A5'>TestCaseID</font>
                            </b>
                        </td>
                        <td width='650' style='word-break:break-all' align='center'>
                            <b>
                                <font id='num_pass' color='#2850A5'>%s  Test %s Passed</font>
                            </b>
                        </td>
                        <td width='150' align='center'>
                            <b>
                                <font color='#2850A5'>Execution Time</font>
                            </b>
                        </td>
                    </tr>
                """ % (
                    bg_color_column,
                    len(passed_cases),
                    "Cases" if len(passed_cases) > 1 else "Case"
                )
                report_file_handler.write(passed_testcase_table)

                for passed_testcase in passed_cases:
                    module_name = passed_testcase.__module__.replace(".", "_") + os.sep + passed_testcase.__class__.__name__
                    module_name_display = passed_testcase.__module__.replace("tests.", "&#x0009;")
                    module_name_display += os.sep + passed_testcase.__class__.__name__

                    report_file_handler.write(
                        "<tr class='all_passed_case' name=%s  width='925'>" % getattr(passed_testcase,
                                                                                      "testcase_filter_tag",
                                                                                      "None"))

                    report_file_handler.write("<td width='125' align='center' >")
                    report_file_handler.write(
                        "<a title='Click to go to test center' href='https://testcenter.lintest.com/testlink/linkto.php?tprojectPrefix=ET&item=testcase&id=ET-%s'> <font color='#2850A5'>" % getattr(
                            passed_testcase, "testcase_id", "None"))
                    report_file_handler.write("%s" % getattr(passed_testcase, "testcase_id", "None"))
                    report_file_handler.write("</font></a>")
                    report_file_handler.write("</td>")

                    report_file_handler.write("<td width='650' style='word-break:break-all'>")
                    report_file_handler.write("<a title='Click to see the log & screenshot' href='")
                    report_file_handler.write(module_name)
                    report_file_handler.write(
                        "'><font color='%s'>" % (
                            "#2850A5" if passed_testcase.rerun_tag == 0 else "green"))
                    report_file_handler.write(module_name_display)

                    # show re-run got passed in report
                    if passed_testcase.rerun_tag == 1:
                        report_file_handler.write("<font color='chocolate'> -- Re-Run Passed</font>")

                    if passed_testcase in error_cases:
                        report_file_handler.write("<font color='orange'> -- Miss Attribute</font>")

                    report_file_handler.write("</font>")
                    report_file_handler.write("</font></a>")

                    try:
                        report_file_handler.write(
                            "<a title='Log' href='%s'>        <font color='green'>&nbsp;&nbsp;Log</font> </a>" %
                            passed_testcase.log_file_path)
                    except BaseException:
                        print(traceback.format_exc())

                    try:
                        if isinstance(passed_testcase, UITestCase):
                            report_file_handler.write(
                                "<a title='Screenshot' href='%s'> <font color='green'> - Screenshot</font> </a>" %
                                passed_testcase.screenshot)
                    except BaseException:
                        traceback.print_exc()
                        print(traceback.format_exc())

                    try:
                        if passed_testcase.rerun_tag == 1:
                            report_file_handler.write(
                                "<a title='ReRun_Log' href='%s'> <font color='green'> | ReRun_Log</font> </a>" %
                                passed_testcase.log_file_path)
                    except BaseException:
                        print(traceback.format_exc())

                    try:
                        if isinstance(passed_testcase, UITestCase):
                            if passed_testcase.rerun_tag == 1:
                                report_file_handler.write(
                                    "<a title='ReRun_Screenshot' href='%s'> <font color='#F18428'> - ReRun_Screenshot</font> </a>" %
                                    passed_testcase.rerun_screenshot)
                    except BaseException:
                        print(traceback.format_exc())

                    report_file_handler.write("</td>")

                    report_file_handler.write("<td width='150' align='center'>")
                    report_file_handler.write("<font color='#2850A5'>")

                    if not hasattr(passed_testcase, "execution_time"):
                        passed_testcase.execution_time = ""

                    report_file_handler.write("%s" % passed_testcase.execution_time)
                    report_file_handler.write("</font>")
                    report_file_handler.write("</td></tr>")
                report_file_handler.write("</table>")

            report_file_handler.write("<br><br>")

            echarts_str = """
            <script>
                    var chartDom = document.getElementById('chart_div');
                   
                    var myChart = echarts.init(chartDom);
                    var option = {
                        title: {
                            text: 'Automation Test Report',
                            left: 'center'
                        },
                        tooltip: {
                             trigger: 'item',
                             formatter: "{a} <br/>{b} : {c} ({d}%%)",
                             axisPointer: {
                               type: 'none'
                             }
                        },
                        legend: {
                         orient: 'vertical',
                         x: 'left',
                         data: ['Passed', 'Failed']
                        },
                        series: [
                            {
                                name: '',
                                type: 'pie',
                                radius: '65%%',
                                data: [
                                    {
                                        value: %s, 
                                        name: 'Passed',
                                        itemStyle: {
                                            color: "#3366CC"
                                        }
                                    },
                                    {
                                        value: %s, 
                                        name: 'Failed', 
                                        itemStyle: {
                                            color: "#DC3912"
                                        }
                                    }
                                ],
                                itemStyle: {
                                 normal: {
                                   label: {
                                     show: true,
                                     formatter: '{b}: {c}  ({d}%%)'
                                   },
                                   labelLine: {
                                     show: true
                                   }
                                 }
                               }
                                
                                
                            }
                        ]
                    };

                    option && myChart.setOption(option);
            </script>
                   """ % (len(passed_cases), failed_cases_count)

            report_file_handler.write(echarts_str)
            report_file_handler.write("</body></html>")
