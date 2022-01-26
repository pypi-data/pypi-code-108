from flask import current_app
from zumidashboard import screen, socketio
from zumidashboard.scripts import check_content_missing
from zumidashboard.updater import check_user_content, copy_content
from zumidashboard.main.utils import awake
from zumidashboard.code_mode.utils import generate_code_editor_lesson_json
from threading import Thread
import os, subprocess, time, json, re


base_dir = '/home/pi/Dashboard/'
usr_dir = '/home/pi/Dashboard/user/'
lib_dir = '/usr/local/lib/python3.5/dist-packages/zumidashboard'

update_user_content_thread = ''


def get_users():
    try:
        usr_list = os.listdir(usr_dir)
        screen.draw_text_center("Please sign in")
        return usr_list
    except FileNotFoundError as e:
        print("get_users() in login/utils.py : {}".format(e))
        os.makedirs(usr_dir)
        return []


def create_new_user(usr_name):
    add_usr_dir = usr_dir + usr_name
    if os.path.isdir(add_usr_dir):
        print("A user already exists")
        return False
    else:
        try:
            os.makedirs(add_usr_dir)
            os.mkdir(add_usr_dir + '/My_Projects')
            os.mkdir(add_usr_dir + '/My_Projects/Jupyter')
            os.mkdir(add_usr_dir + '/My_Projects/Blockly')

            with open("{}/.overlay.json".format(add_usr_dir), "w") as json_file:
                overlaydata = dict()
                overlaydata["main"] = True
                overlaydata["learn"] = True
                json.dump(overlaydata, json_file)

            print("A user has been created : {}".format(usr_name))
            return True
        except Exception as e:
            print("add_user() in login/utils.py : {}".format(e))


def change_user_name(target_user_name, new_user_name):
    target_user_dir = usr_dir + target_user_name
    new_user_dir = usr_dir + new_user_name
    if os.path.isdir(new_user_dir):
        print("Username '{}' already exists".format(new_user_name))
    elif not os.path.isdir(target_user_dir):
        print("Username {} doesn't exist".format(target_user_name))
    else:
        subprocess.Popen(['mv', target_user_dir, new_user_dir])
        print("Changed user name from {} to {}".format(target_user_name, new_user_name))


def delete_user(user_name):
    delete_usr_dir = usr_dir + user_name;
    if os.path.isdir(delete_usr_dir):
        subprocess.Popen(['rm', '-r', delete_usr_dir])


def run_user_jupyter_server(usr_name):
    usr_dir_path = usr_dir + usr_name + '/'
    subprocess.call(['sudo', 'pkill', '-9', 'jupyter'])
    time.sleep(1)
    subprocess.call(['sudo', 'bash', lib_dir + '/shell_scripts/jupyter.sh', usr_dir_path])


def check_overlay(user_name):
    current_usr_dir = usr_dir + user_name
    with open("{}/.overlay.json".format(current_usr_dir), "r") as json_file:
        overlay_data = json.load(json_file)
        return overlay_data


def change_overlay(user_name, item):
    current_usr_dir = usr_dir + user_name
    json_file = open('{}/.overlay.json'.format(current_usr_dir), 'r')
    overlay_data = json.load(json_file)
    overlay_data[item] = False
    json_file.close()
    print(overlay_data)
    with open('{}/.overlay.json'.format(current_usr_dir), 'w') as json_file:
        json.dump(overlay_data, json_file)


def user_login(usr_name):
    global update_user_content_thread

    usr_dir_path = usr_dir + usr_name + '/'
    if current_app.config['USER'] != usr_name:
        current_app.config['USER'] = usr_name
        run_user_jupyter_server(usr_name)
    screen.draw_text_center("Hello, {}!".format(usr_name))
    time.sleep(1)
    awake()

    if check_content_missing(current_app.config['LANGUAGE']):
        socketio.emit('check_content_missing', True)
        socketio.emit("need_update_user_content", False)
        return

    if current_app.config['ERROR_IN_USER_CONTENT'] or check_user_content(base_dir, usr_dir_path, current_app.config['LANGUAGE']):
        socketio.emit("need_update_user_content", True)
        print("start updating user's content")
        time.sleep(3)
        update_user_content_thread = Thread(target=copy_content, args=(base_dir, usr_dir_path, current_app.config['LANGUAGE']))
        update_user_content_thread.start()
    else:
        socketio.emit("need_update_user_content", False)


def update_lessonlist_file(usr_name):
    def change_user_folder_permission(usr_name):
        p = subprocess.Popen(['sudo', 'chown', '-R', 'pi:pi', "/home/pi/Dashboard/user/{}".format(usr_name)])
        p.communicate()
        print("Changed user folder permission")

    change_user_folder_permission(usr_name)
    return dump_lesson_json(usr_name)

    #try:
    #    change_user_folder_permission(usr_name)
    #    time.sleep(1)
    #    return dump_lesson_json(usr_name)
    #except Exception as e:
    #    print(e)
    #    return {"LessonList" : [{"id" : 0, "title" : "Lessons not found", "description" : "I had some issues retrieving the lessons. I might need to reboot."}]}


def dump_lesson_json(usr_name):
    lesson_list = dump_json(usr_name, "Lesson")

    if lesson_list == []:
        return {"LessonList" : [{"id" : 0, "title" : "Lessons not found", "description" : "I had some issues retrieving the lessons. I might need to reboot."}]}
    else:
        return {"LessonList": lesson_list}


def dump_json(usr_name, lesson_type):
    lesson_files_path = "/home/pi/Dashboard/user/{}/Zumi_Content_{}/{}/".format(usr_name, current_app.config['LANGUAGE'], lesson_type)
    beta_code_editor_folder_path = "/home/pi/Dashboard/user/{}/Zumi_Content_{}/NewLesson/".format(usr_name, current_app.config['LANGUAGE'])
    current_user_dir = usr_dir + usr_name + '/'
    complete_data = ''

    if os.path.isdir(beta_code_editor_folder_path):
        if not os.path.exists(current_user_dir + '.code_editor_lesson_{}.json'.format(current_app.config['LANGUAGE'])):
            print('no json file')
            generate_code_editor_lesson_json(current_user_dir)
        complete_json_file = open(current_user_dir + '.code_editor_lesson_{}.json'.format(current_app.config['LANGUAGE']), 'r')
        complete_data = json.load(complete_json_file)

    lesson_folder_files = os.listdir(lesson_files_path)
    lesson_folder_files.sort()
    lesson_list = []
    lesson_id = 0
    for lesson_name in lesson_folder_files:
        if lesson_name[-5:] == 'ipynb':
            description = ''
            beta_file_exists = False
            beta_completed = False
            try:
                with open(lesson_files_path + lesson_name, 'r') as lesson_file:
                    file_content = json.loads(lesson_file.read())
                    for p in file_content["cells"][1]["source"]:
                        p = re.sub(r'#+', '', p)
                        description += re.sub(r'<.*?>', '', p)
                        if len(description) > 175:
                            description = description[:175] + "..."
                            break
                beta_file_exists = check_if_beta_code_editor_lesson_exists(beta_code_editor_folder_path + lesson_name[:-6] + '.md')
                if beta_file_exists:
                    try:
                        beta_completed = complete_data[lesson_name[:-6]]
                    except:
                        # new lesson is not in the .code_editor_lesson.json
                        f = open(current_user_dir + '.code_editor_lesson_{}.json'.format(current_app.config['LANGUAGE']), 'w')
                        complete_data[lesson_name[:-6]] = False
                        json.dump(complete_data, f)
                        f.close()
            except json.decoder.JSONDecodeError:
                print('wrong jupyter format')
                pass
            except Exception as e:
                print(e)
            else:
                lesson_info = {"id": lesson_id, "title": lesson_name[:-6], "description": description, "beta": beta_file_exists, "beta_completed": beta_completed}
                lesson_list.append(lesson_info)
                lesson_id += 1
    return lesson_list


def check_if_beta_code_editor_lesson_exists(file_path):
    return os.path.exists(file_path)


def check_update_user_content_done():
    global update_user_content_thread

    try:
        if update_user_content_thread.is_alive():
            return False
        else:
            return True
    except Exception as e:
        print(e)


def check_jupyter_server():
    p = subprocess.Popen(
        ['sudo', 'bash', lib_dir + '/shell_scripts/check_port.sh', '5555'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    p.wait()
    if len(stdout) > 1:
        print('jupyter server is not ready')
        return False
    else:
        print('jupyter server is ready')
        return True

