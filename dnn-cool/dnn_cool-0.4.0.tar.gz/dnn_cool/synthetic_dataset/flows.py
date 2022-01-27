def body_regression(flow, x, out):
    out += flow.body_x1(x.body_localization)
    out += flow.body_y1(x.body_localization)
    out += flow.body_w(x.body_localization)
    out += flow.body_h(x.body_localization)
    out += flow.shirt_type(x.features)
    return out


def face_regression(flow, x, out):
    out += flow.face_x1(x.face_localization)
    out += flow.face_y1(x.face_localization)
    out += flow.face_w(x.face_localization)
    out += flow.face_h(x.face_localization)
    out += flow.facial_characteristics(x.features)
    return out


def person_regression(flow, x, out):
    out += flow.face_regression(x)
    out += flow.body_regression(x)
    return out


def full_flow(flow, x, out):
    out += flow.camera_blocked(x.features)
    out += flow.door_open(x.features) | (~out.camera_blocked)
    out += flow.door_locked(x.features) | (~out.door_open)
    out += flow.person_present(x.features) | out.door_open
    out += flow.person_regression(x) | out.person_present
    return out