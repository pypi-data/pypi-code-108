import numpy
import numpy as np


def add_random_noise(img):
    n = 40
    i = np.random.randint(0, 64, size=n)
    j = np.random.randint(0, 64, size=n)
    c = np.random.randint(0, 3, size=n)
    values = np.random.randint(0, 255, size=n)
    img[i, j, c] = values


def generate_camera_blocked_image():
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    # randomly add some noise
    add_random_noise(img)
    return img, {'camera_blocked': True}


def generate_door_open_image():
    img = np.ones((64, 64, 3), dtype=np.uint8) * 255
    # randomly add some noise
    add_random_noise(img)
    return img, {'camera_blocked': False, 'door_open': True, 'person_present': False}


def select_facial_characteristics():
    choices = [
        [(255, 0, 255), (0, 2)],
        [(0, 255, 255), (1, 2)],
        [(255, 255, 0), (0, 1)],
        [(0, 0, 0), ()],
        [(255, 0, 0), (0,)],
        [(0, 255, 0), (1,)],
        [(0, 0, 255), (2,)],
    ]
    choice = np.random.randint(0, len(choices), size=1)[0]
    return choices[choice]