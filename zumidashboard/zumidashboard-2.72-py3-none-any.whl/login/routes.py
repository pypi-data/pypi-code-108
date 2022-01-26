from flask import Blueprint, current_app
from zumidashboard import socketio
import zumidashboard.login.utils as utils


login = Blueprint('login', __name__, static_url_path="",
                  static_folder='../dashboard')


base_dir = '/home/pi/Dashboard'
user_dir = '/home/pi/Dashboard/user/'


@login.route('/login')
def login_page():
    return login.send_static_file('index.html')


@socketio.on('get_users')
def _get_users():
    usr_list = utils.get_users()
    socketio.emit('get_users', usr_list)


@socketio.on('set_user')
def set_user(user):
    current_app.config['USER'] = user
    print(current_app.config['USER'])


@socketio.on('add_user')
def _add_user(usr_name):
    succeed = utils.create_new_user(usr_name)


@socketio.on('start_user')
def start_user(usr_name):  # user_login
    utils.user_login(usr_name)


@socketio.on('change_user_name')
def _change_user_name(user_names):
    previous_user_name = user_names[0]
    new_user_name = user_names[1]
    utils.change_user_name(previous_user_name, new_user_name)


@socketio.on('delete_user')
def _delete_user(user_name):
    utils.delete_user(user_name)


@socketio.on('check_overlay')
def _check_overlay(user_name):
    overlay_data = utils.check_overlay(user_name)
    socketio.emit('check_overlay', overlay_data)


@socketio.on('overlay_change')
def overlay_change(user_name, item):
    utils.change_overlay(user_name, item)


@socketio.on('update_lessonlist_file')
def update_lessonlist_file(usr_name):
    lesson_list = utils.update_lessonlist_file(usr_name)
    socketio.emit('update_lessonlist_file', lesson_list)


@socketio.on('check_update_user_content_done')
def _check_update_user_content_done():
    done = utils.check_update_user_content_done()
    socketio.emit('check_update_user_content_done', done)


@socketio.on('check_jupyter_server')
def _check_jupyter_server():
    ready = utils.check_jupyter_server()
    socketio.emit('check_jupyter_server', ready)


@socketio.on('troubleshooting_learn')
def troubleshooting_learn():
    current_app.config['ERROR_IN_USER_CONTENT'] = True
