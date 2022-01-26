from flask import Blueprint, current_app
from zumidashboard import socketio, zumi
import cv2


wizards = Blueprint('wizards', __name__, static_url_path="", static_folder='../dashboard')

knn = ''


@wizards.route('/learning-drive-distance')
def learning_drive_distance():
    return wizards.send_static_file('index.html')


@socketio.on('drive_regression')
def drive_regression(seconds):
    zumi.forward(duration=seconds)


@wizards.route('/learning-colors')
def learning_colors():
    return wizards.send_static_file('index.html')


@socketio.on('start_learning_color')
def start_learning_color():
    global knn

    from zumi.util.color_classifier import ColorClassifier

    knn = ColorClassifier(path='/home/pi/Dashboard/user/'+current_app.config['USER']+'/Data')
    knn.demo_name = "tmp"
    knn.data_file_name = knn.demo_name + "_KNN_data"


@socketio.on('learning_color_label_list')
def learning_color_label_list(label_list):
    global knn

    print(label_list)
    knn.label_num = len(label_list)
    for label in label_list:
        knn.label_names.append(label)
        knn.label_keys.append(label)


@socketio.on('add_color_data')
def add_color_data(label_name):
    global knn

    knn.current_label = label_name
    knn.label_cnt += 1
    try:
        feature = cv2.imread('/home/pi/Dashboard/DriveImg/drivescreen.jpg')

        if not isinstance(feature, list):
            feature = knn.get_hsv_data(feature)

        if feature == [20,0,128]:
            socketio.emit('add_color_data_result', False)
            return

        knn.labels.append(label_name)
        knn.features.append(feature)
        if label_name in knn.data_cnt.keys():
            knn.data_cnt[label_name] += 1
        else:
            knn.data_cnt[label_name] = 1
        socketio.emit('add_color_data_result', feature)
    except Exception as e:
        print(e)
        socketio.emit('add_color_data_result', False)


@socketio.on('color_train')
def color_train():
    global knn

    print(knn.label_num)
    knn.save_data_set()
    knn.get_accuracy()


@socketio.on('knn_fit_hsv')
def knn_fit_hsv():
    global knn

    knn.fit("hsv")


@socketio.on('color_predict')
def color_predict():
    global knn

    try:
        image = cv2.imread('/home/pi/Dashboard/DriveImg/drivescreen.jpg')
        predict = knn.predict(image)
        if not isinstance(image, list):
            feature = knn.get_hsv_data(image)
        socketio.emit('color_predict', {"label": predict, "feature": feature})
    except:
        print('error')


@socketio.on('knn_save_model')
def knn_save_model(model_name):
    global knn

    print(model_name)
    knn.demo_name = model_name
    knn.data_file_name = model_name + "_KNN_data"
    knn.save_data_set()


@wizards.route('/learning-face-detection')
def learning_face_detection():
    return wizards.send_static_file('index.html')

