from functools import partial

import numpy
import numpy as np
import cv2

from dnn_cool.synthetic_dataset.basic_generators import generate_door_open_image, select_facial_characteristics, \
    generate_camera_blocked_image


def generate_door_closed_image(door_locked):
    img, res = generate_door_open_image()

    offsets = np.random.randint(-10, 10, size=4)
    x1, y1 = int(10 + offsets[0]), int(10 + offsets[1])
    x2, y2 = int(50 + offsets[2]), int(50 + offsets[2])

    img = cv2.rectangle(img, (x1, y1), (x2, y2), color=(139, 69, 19), thickness=-1)

    if door_locked:
        lock_start = x1, int((y1 + y2) / 2)
        lock_end = lock_start[0] + 10, lock_start[1] + 10
        img = cv2.rectangle(img, lock_start, lock_end, color=(0, 0, 255), thickness=-1)

    res['door_locked'] = door_locked
    res['camera_blocked'] = False
    res['door_open'] = False
    return img, res


def draw_person(img, res, shirt_type='blue'):
    head_radius = 6
    offsets = np.random.randint(-4, 4, size=4)
    head = int(30 + offsets[0]), int(10 + offsets[1])

    color, face_characteristics = select_facial_characteristics()
    img = cv2.circle(img, head, head_radius, color=color, thickness=-1)

    res['person_present'] = True
    res['person_regression.face_regression.face_x1'] = head[0] - head_radius
    res['person_regression.face_regression.face_y1'] = head[1] - head_radius
    res['person_regression.face_regression.face_w'] = 2 * head_radius
    res['person_regression.face_regression.face_h'] = 2 * head_radius
    res['person_regression.face_regression.facial_characteristics'] = ','.join(map(str, face_characteristics))

    offsets = np.random.randint(-2, 2, size=4)
    d = head_radius * 2
    rec_start = head[0] - head_radius + offsets[0], head[1] + head_radius + offsets[1]
    rec_end = rec_start[0] + d + offsets[2], rec_start[1] + 30 + offsets[3]

    if shirt_type == 'blue':
        color = (0, 0, 255)
        shirt_label = 0
    elif shirt_type == 'red':
        color = (255, 0, 0)
        shirt_label = 1
    elif shirt_type == 'yellow':
        color = (255, 255, 0)
        shirt_label = 2
    elif shirt_type == 'cyan':
        color = (0, 255, 255)
        shirt_label = 3
    elif shirt_type == 'magenta':
        color = (255, 0, 255)
        shirt_label = 4
    elif shirt_type == 'green':
        color = (0, 255, 0)
        shirt_label = 5
    else:
        # black
        color = (0, 0, 0)
        shirt_label = 6

    cv2.rectangle(img, rec_start, rec_end, color=color, thickness=-1)

    res['person_regression.body_regression.body_x1'] = rec_start[0]
    res['person_regression.body_regression.body_y1'] = rec_start[1]
    res['person_regression.body_regression.body_w'] = rec_end[0] - rec_start[0]
    res['person_regression.body_regression.body_h'] = rec_end[1] - rec_start[1]
    res['person_regression.body_regression.shirt_type'] = shirt_label

    return img, res


def generate_image_with_person(shirt_type='blue'):
    img, res = generate_door_open_image()
    img, res = draw_person(img, res, shirt_type)
    return img, res


def generate_sample():
    generators = [generate_camera_blocked_image,
                  generate_door_open_image,
                  partial(generate_door_closed_image, door_locked=True),
                  partial(generate_door_closed_image, door_locked=False),
                  partial(generate_image_with_person, shirt_type='blue'),
                  partial(generate_image_with_person, shirt_type='red'),
                  partial(generate_image_with_person, shirt_type='yellow'),
                  partial(generate_image_with_person, shirt_type='cyan'),
                  partial(generate_image_with_person, shirt_type='magenta'),
                  partial(generate_image_with_person, shirt_type='green'),
                  partial(generate_image_with_person, shirt_type='black')
                  ]
    choice = np.random.randint(0, len(generators), size=1)[0]
    return generators[choice]()