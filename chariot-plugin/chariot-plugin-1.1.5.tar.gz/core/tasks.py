import os
import json

from .config import *
from .tools import Tools



tools = Tools()


def generate(path: str, yml: str):
    """
    生成插件
    """

    # 验证路径，　是否是yaml文件
    yml_path = os.path.join(path, yml)
    if not any([yml.endswith(y) for y in ["yml", "yaml"]]) or not os.path.exists(yml_path):
        logging.error(f"yaml路径错误 - {yml_path}")
        return
    else:
        yaml_data = tools.readYaml(yml_path)
        logging.info(f"readed {yml}")

    plugin_name = yaml_data.get("name", "hah")
    actions_class_list = []
    triggers_class_list = []
    indicator_receivers_class_list = []
    alarm_receivers_class_list = []

    # 当前文件路劲下生成sdk
    tar_path = os.path.join(BASE_DIR, os.path.join("res", "demo.tar.gz"))
    target_path = path
    tools.tarExtract(tar_path, target_path)

    # 读取types
    types = yaml_data.get("types")
    typesTemp = ""
    if types:
        for types_name, types_data in types.items():
            typesData = {
                "className": tools.getModelName(types_name),
                "args": tools.ymlTransPy(types_data)
            }
            typesTemp += tools.renderStrTemplate(typesData, MODELTEMPLATE)


    # 读取connection
    connection = yaml_data.get("connection")
    connection = {
                "className": tools.getModelName("connection"),
                "args": tools.ymlTransPy(connection)
            }
    connTemp = tools.renderStrTemplate(connection, MODELTEMPLATE)

    # 创建tests
    tests_path = os.path.join(path, "tests")
    if not os.path.exists(tests_path):
        os.mkdir(tests_path)


    # 生成actions
    actions = yaml_data.get("actions")
    if actions:
        actions_path = os.path.join(path, "actions")
        if not os.path.exists(actions_path):
            os.mkdir(actions_path)

        actionsTemp = ""
        actionsModelTemp = ""
        actionsModelTemp += modelHeader
        actionsModelTemp += typesTemp
        actionsModelTemp += connTemp


        init_list = []

        for title, data in actions.items():

            # models
            inp = data.get("input")
            outp = data.get("output")

            actionsName = tools.getModelName(title, "Actions")
            inpClassName = tools.getModelName(title, "Input")
            outpClassName = tools.getModelName(title, "Output")

            actions_class_list.append(actionsName)
            init_list.append([
                title,
                actionsName
            ])

            inp_data = {
                "className": inpClassName,
                "args": tools.ymlTransPy(inp)
            }
            outp_data = {
                "className": outpClassName,
                "args": tools.ymlTransPy(outp)
            }

            inpTemp = tools.renderStrTemplate(inp_data, MODELTEMPLATE)
            outpTemp = tools.renderStrTemplate(outp_data, MODELTEMPLATE)

            # model主要内容
            actionsModelTemp += inpTemp
            actionsModelTemp += outpTemp

            # action
            actionData = {
                "actionsName": actionsName,
                "name": title,
                "inputModel": inpClassName,
                "outputModel": outpClassName,
                "connModel": tools.getModelName("connection"),
            }
            actionsTemp = tools.renderStrTemplate(actionData, ACTIONTEMPLATE)

            file_path = os.path.join(actions_path, f"{title}.py")
            if not os.path.exists(file_path):
                tools.writeFile(actionsTemp, file_path)
                logging.info(f"gnerated actions/{title}.py ok")

            # 生成测试文件
            file_path = os.path.join(tests_path, f"{title}.json")
            testData = tools.renderStrTemplate({"title": title}, ACTIONSTESTTEMPLATE)
            tools.writeFile(testData, file_path)
            logging.info(f"generated tests/{title}.json ok")

        # 生成__init__.py
        file_path = os.path.join(actions_path, "__init__.py")
        initData = tools.renderStrTemplate({"init_list": init_list}, INITTEMPLATE)
        tools.writeFile(initData, file_path)
        logging.info(f"generated actions/__init__.py ok")

        file_path = os.path.join(actions_path, "models.py")
        tools.writeFile(actionsModelTemp, file_path)
        logging.info(f"gnerated actions/models.py ok")

    #===

    # 生成triggers
    triggers = yaml_data.get("triggers")
    if triggers:
        triggers_path = os.path.join(path, "triggers")
        if not os.path.exists(triggers_path):
            os.mkdir(triggers_path)

        triggersTemp = ""
        triggersModelTemp = ""
        triggersModelTemp += modelHeader
        triggersModelTemp += typesTemp
        triggersModelTemp += connTemp


        init_list = []

        for title, data in triggers.items():

            # models
            inp = data.get("input")
            outp = data.get("output")

            triggersName = tools.getModelName(title, "Triggers")
            inpClassName = tools.getModelName(title, "Input")
            outpClassName = tools.getModelName(title, "Output")

            triggers_class_list.append(triggersName)
            init_list.append([
                title,
                triggersName
            ])

            inp_data = {
                "className": inpClassName,
                "args": tools.ymlTransPy(inp)
            }
            outp_data = {
                "className": outpClassName,
                "args": tools.ymlTransPy(outp)
            }

            inpTemp = tools.renderStrTemplate(inp_data, MODELTEMPLATE)
            outpTemp = tools.renderStrTemplate(outp_data, MODELTEMPLATE)

            # model主要内容
            triggersModelTemp += inpTemp
            triggersModelTemp += outpTemp

            # trigger
            triggerData = {
                "triggersName": triggersName,
                "name": title,
                "inputModel": inpClassName,
                "outputModel": outpClassName,
                "connModel": tools.getModelName("connection"),
            }
            triggersTemp = tools.renderStrTemplate(triggerData, TRIGGERSTEMPLATE)

            file_path = os.path.join(triggers_path, f"{title}.py")
            if not os.path.exists(file_path):
                tools.writeFile(triggersTemp, file_path)
                logging.info(f"gnerated triggers/{title}.py ok")

            # 生成测试文件
            file_path = os.path.join(tests_path, f"{title}.json")
            testData = tools.renderStrTemplate({"title": title}, TRIGGERSTESTTEMPLATE)
            tools.writeFile(testData, file_path)
            logging.info(f"generated tests/{title}.json ok")

        # 生成__init__.py
        file_path = os.path.join(triggers_path, "__init__.py")
        initData = tools.renderStrTemplate({"init_list": init_list}, INITTEMPLATE)
        tools.writeFile(initData, file_path)
        logging.info(f"generated triggers/__init__.py ok")


        file_path = os.path.join(triggers_path, "models.py")
        tools.writeFile(triggersModelTemp, file_path)
        logging.info(f"gnerated triggers/models.py ok")

    #===


    # 生成indicator_receivers
    indicator_receivers = yaml_data.get("indicator_receivers")
    if indicator_receivers:
        indicator_receivers_path = os.path.join(path, "indicator_receivers")
        if not os.path.exists(indicator_receivers_path):
            os.mkdir(indicator_receivers_path)

        indicator_receiversTemp = ""
        indicator_receiversModelTemp = ""
        indicator_receiversModelTemp += modelHeader
        indicator_receiversModelTemp += INDICATORRECEIVERSMODELTYPES
        indicator_receiversModelTemp += typesTemp
        indicator_receiversModelTemp += connTemp


        init_list = []

        for title, data in indicator_receivers.items():

            # models
            inp = data.get("input")

            indicator_receiversName = tools.getModelName(title, "indicator_receivers")
            inpClassName = tools.getModelName(title, "Input")
            outpClassName = tools.getModelName(title, "Output")

            indicator_receivers_class_list.append(indicator_receiversName)
            init_list.append([
                title,
                indicator_receiversName
            ])

            inp_data = {
                "className": inpClassName,
                "args": tools.ymlTransPy(inp)
            }
            outp_data = {
                "className": outpClassName,
            }

            inpTemp = tools.renderStrTemplate(inp_data, MODELTEMPLATE)
            outpTemp = tools.renderStrTemplate(outp_data, INDICATORRECEIVERSMODELTEMPLATE)

            # model主要内容
            indicator_receiversModelTemp += inpTemp
            indicator_receiversModelTemp += outpTemp

            # indicator_receiver
            indicator_receiverData = {
                "indicator_receiversName": indicator_receiversName,
                "name": title,
                "inputModel": inpClassName,
                "outputModel": outpClassName,
                "connModel": tools.getModelName("connection"),
            }
            indicator_receiversTemp = tools.renderStrTemplate(indicator_receiverData, INDICATORRECEIVERSTEMPLATE)

            file_path = os.path.join(indicator_receivers_path, f"{title}.py")
            if not os.path.exists(file_path):
                tools.writeFile(indicator_receiversTemp, file_path)
                logging.info(f"gnerated indicator_receivers/{title}.py ok")

            # 生成测试文件
            file_path = os.path.join(tests_path, f"{title}.json")
            testData = tools.renderStrTemplate({"title": title}, INDICATORRECEIVERSTESTTEMPLATE)
            tools.writeFile(testData, file_path)
            logging.info(f"generated tests/{title}.json ok")

        # 生成__init__.py
        file_path = os.path.join(indicator_receivers_path, "__init__.py")
        initData = tools.renderStrTemplate({"init_list": init_list}, INITTEMPLATE)
        tools.writeFile(initData, file_path)
        logging.info(f"generated indicator_receivers/__init__.py ok")

        file_path = os.path.join(indicator_receivers_path, "models.py")
        tools.writeFile(indicator_receiversModelTemp, file_path)
        logging.info(f"gnerated indicator_receivers/models.py ok")

    #===



    # 生成alarm_receivers
    alarm_receivers = yaml_data.get("alarm_receivers")
    if alarm_receivers:
        alarm_receivers_path = os.path.join(path, "alarm_receivers")
        if not os.path.exists(alarm_receivers_path):
            os.mkdir(alarm_receivers_path)

        alarm_receiversTemp = ""
        alarm_receiversModelTemp = ""
        alarm_receiversModelTemp += modelHeader
        alarm_receiversModelTemp += ALARMRECEIVERSMODELTYPES
        alarm_receiversModelTemp += typesTemp
        alarm_receiversModelTemp += connTemp

        init_list = []

        for title, data in alarm_receivers.items():

            # models
            inp = data.get("input")

            alarm_receiversName = tools.getModelName(title, "alarm_receivers")
            inpClassName = tools.getModelName(title, "Input")
            outpClassName = tools.getModelName(title, "Output")

            alarm_receivers_class_list.append(alarm_receiversName)
            init_list.append([
                title,
                alarm_receiversName
            ])

            inp_data = {
                "className": inpClassName,
                "args": tools.ymlTransPy(inp)
            }
            outp_data = {
                "className": outpClassName,
            }

            inpTemp = tools.renderStrTemplate(inp_data, MODELTEMPLATE)
            outpTemp = tools.renderStrTemplate(outp_data, ALARMRECEIVERSMODELTEMPLATE)

            # model主要内容
            alarm_receiversModelTemp += inpTemp
            alarm_receiversModelTemp += outpTemp

            # alarm_receiver
            alarm_receiverData = {
                "alarm_receiversName": alarm_receiversName,
                "name": title,
                "inputModel": inpClassName,
                "outputModel": outpClassName,
                "connModel": tools.getModelName("connection"),
            }
            alarm_receiversTemp = tools.renderStrTemplate(alarm_receiverData, ALARMRECEIVERSTEMPLATE)

            file_path = os.path.join(alarm_receivers_path, f"{title}.py")
            if not os.path.exists(file_path):
                tools.writeFile(alarm_receiversTemp, file_path)
                logging.info(f"gnerated alarm_receivers/{title}.py ok")

            # 生成测试文件
            file_path = os.path.join(tests_path, f"{title}.json")
            testData = tools.renderStrTemplate({"title": title}, ALARMRECEIVERSTESTTEMPLATE)
            tools.writeFile(testData, file_path)
            logging.info(f"generated tests/{title}.json ok")

        # 生成__init__.py
        file_path = os.path.join(alarm_receivers_path, "__init__.py")
        initData = tools.renderStrTemplate({"init_list": init_list}, INITTEMPLATE)
        tools.writeFile(initData, file_path)
        logging.info(f"generated alarm/__init__.py ok")

        file_path = os.path.join(alarm_receivers_path, "models.py")
        tools.writeFile(alarm_receiversModelTemp, file_path)
        logging.info(f"gnerated alarm_receivers/models.py ok")

    # ===


    # 创建入口文件　main.py
    mainData = {
        "pluginName": tools.getModelName(plugin_name, "Plugin").replace(" ", "_"),
        "actionClassees": actions_class_list,
        "triggerClassees": triggers_class_list,
        "indicatorReceiverClassees": indicator_receivers_class_list,
        "alarmReceiverClassees": alarm_receivers_class_list
    }
    file_path = os.path.join(path, "main.py")
    mainTemp = tools.renderStrTemplate(mainData, MAINTEMPLATE)
    tools.writeFile(mainTemp, file_path)
    logging.info(f"generated main.py ok")


    # 创建help.md
    helpData = yaml_data
    file_path = os.path.join(path, "help.md")
    mainTemp = tools.renderStrTemplate(helpData, HELPTEMPLATE)
    tools.writeFile(mainTemp, file_path)
    logging.info("generated help.md ok")

    # 生成util
    util_path = os.path.join(path, "util")
    if not os.path.exists(util_path):
        os.mkdir(util_path)
        logging.info("generated util ok")

    logging.info("All things done successfully ^_^")


def run(path: str, tests: str):

    main_path = os.path.join(path, "main.py")
    tests_path = os.path.join(path, tests)

    if not os.path.exists(tests_path):
        logging.error(f"请正确输入路径")


    cmd = f"python {main_path} run < {tests_path}"
    os.system(cmd)

def http(path: str):
    main_path = os.path.join(path, "main.py")


    cmd = f"python {main_path} http"
    os.system(cmd)

def test(path: str, tests: str):
    main_path = os.path.join(path, "main.py")
    tests_path = os.path.join(path, tests)

    if not os.path.exists(tests_path):
        logging.error(f"请正确输入路径")

    cmd = f"python {main_path} test < {tests_path}"
    os.system(cmd)

def tarball(path: str):

    Makefile_path = os.path.join(path, "Makefile")
    if os.path.exists(Makefile_path):
        cmd = "make tarball"
        os.system(cmd)


def mkimg(path: str):
    Makefile_path = os.path.join(path, "Makefile")
    if os.path.exists(Makefile_path):
        cmd = "make image"
        os.system(cmd)


