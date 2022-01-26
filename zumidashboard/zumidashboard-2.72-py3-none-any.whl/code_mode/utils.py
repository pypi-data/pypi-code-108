from flask import current_app
import os
import subprocess
import time
import json
import base64
import textwrap
import re


lib_dir = '/usr/local/lib/python3.5/dist-packages/zumidashboard/'
usr_dir = '/home/pi/Dashboard/user/'

is_new_blockly_project = False


def load_code_mode_projects(user_name):
    blockly = os.listdir(usr_dir + user_name + '/My_Projects/Blockly')
    jupyter = [file.split(".ipynb")[0] for file in os.listdir(usr_dir + user_name + '/My_Projects/Jupyter') if
               file.endswith(".ipynb")]

    return {"jupyter": jupyter, "blockly": blockly}


def create_new_jupyter(user_name, project_name):
    jupyter_folder = "{}/My_Projects/Jupyter/".format(usr_dir + user_name)
    subprocess.call(['cp', lib_dir + 'shell_scripts/Untitled.ipynb', jupyter_folder])
    time.sleep(1)
    subprocess.call(['mv', "{}Untitled.ipynb".format(jupyter_folder), "{}{}.ipynb".format(jupyter_folder, project_name)])
    time.sleep(1.5)
    subprocess.Popen(['sudo', 'chown', '-R', 'pi', jupyter_folder])


def rename_jupyter(user_name, project_name, new_name):
    jupyter_dir = "{}/My_Projects/Jupyter/".format(usr_dir + user_name)
    subprocess.call(['mv', "{}.ipynb".format(jupyter_dir+project_name), "{}.ipynb".format(jupyter_dir+new_name)])
    time.sleep(1)


def delete_jupyter(user_name, project_name):
    blockly_dir = "{}/My_Projects/Jupyter/".format(usr_dir + user_name)
    subprocess.call(['rm',"-rf", "{}.ipynb".format(blockly_dir + project_name)])
    time.sleep(1)


def create_blockly(user_name, project_name):
    global is_new_blockly_project

    is_new_blockly_project = True
    myfile = open("{}/My_Projects/Blockly/{}.xml".format(usr_dir + user_name, project_name), 'w')
    myfile.close()


def rename_blockly(user_name, project_name, new_name):
    blockly_dir = "{}/My_Projects/Blockly/".format(usr_dir + user_name)
    subprocess.call(['mv', "{}.xml".format(blockly_dir+project_name), "{}.xml".format(blockly_dir+new_name)])
    time.sleep(1)


def delete_blockly(user_name, project_name):
    blockly_dir = "{}/My_Projects/Blockly/".format(usr_dir + user_name)
    subprocess.call(['rm',"-rf", "{}.xml".format(blockly_dir + project_name)])
    time.sleep(1)


def load_blockly_project(user_name, project_name):
    global is_new_blockly_project

    print('app: get xml project')
    if is_new_blockly_project:
        is_new_blockly_project = False
        return ''
    else:
        project_file = open("{}/My_Projects/Blockly/{}.xml".format(usr_dir + user_name, project_name), 'r')
        return str(project_file.read())


def save_blockly_file(user_name, project_name, xml_content):
    print('Saved blockly file')
    myfile = open("{}/My_Projects/Blockly/{}.xml".format(usr_dir + user_name, project_name), 'w')
    myfile.write(xml_content)
    myfile.close()


def blockly_load_knn_models(user):
    from zumi.util.color_classifier import ColorClassifier
    knn = ColorClassifier(path='/home/pi/Dashboard/user/' + user + '/Data')

    model_path = '/home/pi/Dashboard/user/'+user+'/Data/color-classifier/'
    model_list = os.listdir(model_path)

    models = []

    for model in model_list:
        txt_path = model_path + model + '/' + model + '_KNN_data.txt'
        if os.path.isfile(txt_path) is False:
            continue
        knn.demo_name = model
        knn.data_file_name = knn.demo_name + "_KNN_data"
        knn.load_model(model)
        labels = knn.label_names
        models.append({'name': model, 'labels': labels})
        knn.label_names = []
    return models


def run_blockly(source_code_base64):
    message_deco = base64.b64decode(source_code_base64)
    message_deco = message_deco.decode("utf-8")

    new_path = '/home/pi/blockly.py'
    new_days = open(new_path, 'w+')
    message_deco = """try:
  import sys, traceback
""" + textwrap.indent(message_deco, 2 * ' ') + """  print("endfile")
  if 'camera' in locals():
    camera.close()
except KeyboardInterrupt:
  print("Shutdown requested...exiting")
except Exception:
  print("endfile")
  traceback.print_exc(file=sys.stdout)
  if 'camera' in locals():
    camera.close()
  zumi.stop()
sys.exit(0)"""
    new_days.write(message_deco)
    new_days.close()

    try:
        subprocess.Popen(['fuser', '-k', '3456/tcp'])
        time.sleep(0.1)
    except:
        print('streaming server is closed')
    finally:
        return True


def get_image_data(i):
    file_path = '/usr/local/lib/python3.5/dist-packages/zumidashboard/dashboard/code_editor_image' + str(i)  + '.jpg'
    data = get_base64_data(file_path)
    return data


def get_base64_data(file_path):
    try:
        with open(file_path, 'rb') as f:
            b = base64.b64encode(f.read())
            blob_image = b.decode('utf-8')
            return blob_image
    except Exception as e:
        print(file_name)
        print(e)
        return ''


def is_lesson_completed(title):
    if current_app.config['USER'] == "":
        return
    current_user_dir = usr_dir + current_app.config['USER'] + '/'
    if not os.path.exists(current_user_dir + '.code_editor_lesson_{}.json'.format(current_app.config['LANGUAGE'])):
        print('no json file')
        generate_code_editor_lesson_json(current_user_dir)
        return False
    with open(current_user_dir + '.code_editor_lesson_{}.json'.format(current_app.config['LANGUAGE']), 'r') as json_file:
        complete_data = json.load(json_file)
        print(complete_data)
        return complete_data[title]


def generate_code_editor_lesson_json(current_user_dir):
    print('code_mode/utils.py : generate code editor lesson json')
    lesson_dir_path = "{}/Zumi_Content_{}/NewLesson/".format(current_user_dir, current_app.config['LANGUAGE'])
    if not os.path.isdir(lesson_dir_path):
        print("Please update Zumi Content")
        return
    with open("{}/.code_editor_lesson_{}.json".format(current_user_dir, current_app.config['LANGUAGE']), "w") as f:
        json_data = dict()
        lesson_list = os.listdir(lesson_dir_path)
        lesson_list.sort()
        for lesson_name in lesson_list:
            json_data[lesson_name.replace('.md', '')] = False
        json.dump(json_data, f)


def mark_lesson_as(title, completed):
    current_user_dir = usr_dir + current_app.config['USER'] + '/'
    complete_data = {}
    with open("{}/.code_editor_lesson_{}.json".format(current_user_dir, current_app.config['LANGUAGE']), "r") as f:
        complete_data = json.load(f)
        complete_data[title] = completed
    print(complete_data)
    with open("{}/.code_editor_lesson_{}.json".format(current_user_dir, current_app.config['LANGUAGE']), "w") as f:
        json.dump(complete_data, f)


def run_code_editor(source_code_base64):
    message_deco = base64.b64decode(source_code_base64)
    message_deco = message_deco.decode("utf-8")
    current_app.socketXterm.emit(
        "pty-input", {"input": "{}\n".format(message_deco)}, namespace='/pty')


def image_path_in(lesson_line):
    return True if "![" in lesson_line else False


def get_image_path_and_format(lesson_line):
    # image_name = re.findall('\[\w+\]', lesson_line)[0].replace("[", "").replace("]","")
    image_path = re.findall('\(.+\)', lesson_line)[0].replace("(", "").replace(")","")
    tmp = image_path.split('.')
    image_format = tmp[len(tmp)-1]
    return image_path, image_format


def get_lesson_image(file_name):
    file_path = '/home/pi/Dashboard/user/' + current_app.config['USER'] + '/Zumi_Content_' + current_app.config['LANGUAGE'] + '/Data/images/' + file_name
    try:
        with open(file_path, 'rb') as f:
            b = base64.b64encode(f.read())
            blob_image = b.decode('utf-8')
            return blob_image
    except Exception as e:
        print(file_name)
        print(e)
        return ''
