from flask import Blueprint, request, current_app
from zumidashboard import socketio
from zumidashboard.login.routes import update_lessonlist_file
import zumidashboard.code_mode.utils as utils


code_mode = Blueprint('code_mode', __name__, static_url_path="", static_folder='../dashboard')

running_code_sid = ''


@code_mode.route('/code-mode')
def code_mode_page():
    return code_mode.send_static_file('index.html')


@code_mode.route('/blockly')
def blockly_page():
    return code_mode.send_static_file('index.html')


@code_mode.route('/zumi-code-editor')
def zumi_code_editor_page():
    return code_mode.send_static_file('index.html')


@code_mode.route('/zumi-code-editor-lesson')
def zumi_code_editor_lesson_page():
    return code_mode.send_static_file('index.html')


@socketio.on('code_mode')
def load_code_mode_projects(user_name):
    projects = utils.load_code_mode_projects(user_name)
    socketio.emit('code_mode', projects)


@socketio.on('create_jupyter')
def create_jupyter(user_name, project_name):
    utils.create_new_jupyter(user_name, project_name)


@socketio.on('rename_jupyter')
def rename_jupyter(user_name, project_name, new_name):
    utils.rename_jupyter(user_name, project_name, new_name)


@socketio.on('delete_jupyter')
def delete_jupyter(user_name, project_name):
    utils.delete_jupyter(user_name, project_name)


@socketio.on('create_blockly')
def create_blockly(user_name, project_name):
    utils.create_blockly(user_name, project_name)


@socketio.on('rename_blockly')
def rename_blockly(user_name, project_name, new_name):
    utils.rename_blockly(user_name, project_name, new_name)


@socketio.on('delete_blockly')
def delete_blockly(user_name, project_name):
    utils.delete_blockly(user_name, project_name)


@socketio.on('get_blockly_project')
def get_blockly_project(user_name, project_name):
    xml = utils.load_blockly_project(user_name, project_name)
    if xml == '':
        socketio.emit('get_blockly_project', '')
    else:
        socketio.emit('get_blockly_project', [user_name, project_name, xml])


@socketio.on('save_blockly_file')
def save_blockly_file(user_name, project_name, xml_content):
    utils.save_blockly_file(user_name, project_name, xml_content)


@socketio.on('get_knn_model')
def get_knn_model(user):
    models = utils.blockly_load_knn_models(user)
    socketio.emit('get_knn_model', models)


@socketio.on('run_blockly')
def run_blockly(source_code_base64):
    global running_code_sid

    running_code_sid = request.sid
    socketio.emit('code_is_running', running_code_sid)
    result = utils.run_blockly(source_code_base64)
    if result:
        current_app.socketXterm.emit(
        "pty-input", {"input": "python3 /home/pi/blockly.py\n"}, namespace='/pty')


@socketio.on('endfile')
def end_file(data):
    print('end file')
    socketio.emit('ended_running_blockly', '')


@socketio.on('show_image')
def show_image(i):
    global running_code_sid
    print('code_mode : show image')
    data = utils.get_image_data(i)
    socketio.emit('show_image', [data, running_code_sid])


@socketio.on('stop')
def stop():
    current_app.socketXterm.emit("pty-input", {"input": "\x03"}, namespace='/pty')
    socketio.emit('ended_running_blockly', '')


# TODO decide way to send multiple way
# we can make sending with tag as well
@socketio.on('read_lesson_file')
def read_lesson_file(lesson_name):
    file_content = ""
    file_path = '/home/pi/Dashboard/user/' + current_app.config['USER'] + \
        '/Zumi_Content_en/NewLesson/' + lesson_name + ".md"
    with open(file_path) as lesson:
        for line in lesson.readlines():
            if utils.image_path_in(line):
                file_name, file_format = utils.get_image_path_and_format(line)
                blob_image = utils.get_lesson_image(file_name)
                line = line.replace(file_name, 'data:image/' + file_format + ';base64,' + blob_image)
            file_content += line
    # # option 1 send through socket directly
    socketio.emit("read_lesson_file", file_content.split("***\n"))
    # socketio.emit("read_lesson_file", {"lesson": file_content})
    # # option 2
    # with open('someware current lesson file read', 'w') as lesson_json:
    #     json.dump({"lesson": file_content}, lesson_json)


@socketio.on('is_lesson_complete')
def is_lesson_complete(title):
    is_completed = utils.is_lesson_completed(title)
    socketio.emit('is_lesson_complete', is_completed)


@socketio.on('mark_lesson_as')
def mark_lesson_as(title, completed):
    utils.mark_lesson_as(title, completed)
    update_lessonlist_file(current_app.config['USER'])


@socketio.on('run_code_editor')
def run_code_editor(source_code_base64):
    utils.run_code_editor(source_code_base64)
#    global running_code_sid

#    running_code_sid = request.sid
#    socketio.emit('code_is_running', running_code_sid)
#    message_deco = base64.b64decode(source_code_base64)
#    message_deco = message_deco.decode("utf-8")
#    current_app.socketXterm.emit(
#        "pty-input", {"input": "{}\n".format(message_deco)}, namespace='/pty')
#    if result:
#        current_app.socketXterm.emit(
#        "pty-input", {"input": "python3 /home/pi/blockly.py\n"}, namespace='/pty')
