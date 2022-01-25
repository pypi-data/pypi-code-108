# -*- coding: utf-8 -*-
# @Time     : 2021/6/2 10:24
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : quanternion.py
# @Version  : Python 3.8.5 +
import math


def q_update(acc, w, q, SamplePeriod=1 / 20, Beta=0.1):
    ax, ay, az = acc
    gx, gy, gz = w
    gx = gx / 180 * math.pi
    gy = gy / 180 * math.pi
    gz = gz / 180 * math.pi
    q1 = q[0]
    q2 = q[1]
    q3 = q[2]
    q4 = q[3]

    _2q1 = 2 * q1
    _2q2 = 2 * q2
    _2q3 = 2 * q3
    _2q4 = 2 * q4
    _4q1 = 4 * q1
    _4q2 = 4 * q2
    _4q3 = 4 * q3
    _8q2 = 8 * q2
    _8q3 = 8 * q3
    q1q1 = q1 * q1
    q2q2 = q2 * q2
    q3q3 = q3 * q3
    q4q4 = q4 * q4

    norm = math.sqrt(ax * ax + ay * ay + az * az)
    if norm == 0.0:
        return
    norm = 1 / norm
    ax *= norm
    ay *= norm
    az *= norm

    s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
    s2 = _4q2 * q4q4 - _2q4 * ax + 4 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
    s3 = 4 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
    s4 = 4 * q2q2 * q4 - _2q2 * ax + 4 * q3q3 * q4 - _2q3 * ay

    norm = 1 / math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)
    s1 *= norm
    s2 *= norm
    s3 *= norm
    s4 *= norm

    qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - Beta * s1
    qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - Beta * s2
    qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - Beta * s3
    qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - Beta * s4

    q1 += qDot1 * SamplePeriod
    q2 += qDot2 * SamplePeriod
    q3 += qDot3 * SamplePeriod
    q4 += qDot4 * SamplePeriod

    norm = 1 / math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)

    q[0] = q1 * norm
    q[1] = q2 * norm
    q[2] = q3 * norm
    q[3] = q4 * norm
    return


# quaternion to pitch, roll, yaw in rad
# !! May have ranging problem, use carefully
def q_to_euler(q):
    alpha = math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2]))
    beta = math.asin(2 * (q[0] * q[2] - q[3] * q[1]))
    psi = math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3]))

    return alpha, beta, psi


def kalman_filter(acc, w, last_prediction, last_v, period=20):
    alpha, beta, _ = last_prediction
    x, y, z = acc
    gx, gy, gz = w
    last_a, last_a_m, last_b, last_b_m = last_v
    kg_a = math.sqrt((last_a * last_a) / (last_a * last_a + last_a_m * last_a_m))
    kg_b = math.sqrt((last_b * last_b) / (last_b * last_b + last_b_m * last_b_m))

    alpha_p = alpha + gx * 1.0 / period
    beta_p = beta + gy * 1.0 / period

    alpha_me = math.atan(y / z) / math.pi * 180
    beta_me = math.asin(-x / 1.0) / math.pi * 180

    alpha_fin = alpha_p + kg_a * (alpha_me - alpha_p)
    beta_fin = beta_p + kg_b * (beta_me - beta_p)

    a_v = math.sqrt((1 - kg_a) * last_a * last_a)
    a_m = alpha_fin - alpha_me

    b_v = math.sqrt((1 - kg_b) * last_b * last_b)
    b_m = beta_fin - beta_me

    return (alpha_fin, beta_fin, 0.0), (a_v, a_m, b_v, b_m)


def kalman_filter_2(acc, w, previous, previous_p, q=1e-6, r=1e-1, period=20):
    alpha, beta, theta = previous
    p_alpha, p_beta = previous_p
    x, y, z = acc
    gx, gy, gz = w

    alpha_p = alpha + gx * 1.0 / period
    beta_p = beta + gy * 1.0 / period

    alpha_me = math.atan(y / z) / math.pi * 180
    beta_me = math.asin(-x / 1.0) / math.pi * 180

    noise_a = p_alpha + q
    noise_b = p_beta + q

    kg_a = noise_a / (noise_a + r)
    kg_b = noise_b / (noise_b + r)

    opt_alpha = alpha_p + kg_a * (alpha_me - alpha_p)
    opt_beta = beta_p + kg_b * (beta_me - beta_p)

    p_alpha_next = (1 - kg_a) * noise_a
    p_beta_next = (1 - kg_b) * noise_b

    return (opt_alpha, opt_beta, theta), (p_alpha_next, p_beta_next)


def q_update_by_madgwickahrs(acc, w, angles):
    angles.update_imu(w, acc)
    r, p, y = angles.quaternion.to_euler_angles()
    rpy = (r / math.pi * 180, p / math.pi * 180, y / math.pi * 180)
    return rpy


def kalman_filter_self(acc, w, previous_angle, previous_p, r_val=None):
    if r_val is None:
        r_val = 2
    x, y, z = acc
    alpha, beta, theta = previous_angle

    z_value = [0, 0, 0]
    x_value = [0, 0, 0]
    x_hat = [0, 0, 0]

    k = [0, 0, 0]
    p_hat = [0, 0, 0]
    for i in range(3):
        k[i] = previous_p[i] / (previous_p[i] + r_val)

    for i in range(3):
        p_hat[i] = previous_p[i] * (1 - k[i])

    z_value[0] = math.atan(y / z) / math.pi * 180
    z_value[1] = math.asin(-x / 1.0) / math.pi * 180
    z_value[2] = theta

    for i in range(3):
        x_value[i] = previous_angle[i] + w[i] * 1 / 20

    for i in range(3):
        x_hat[i] = x_value[i] + k[i] * (z_value[i] - x_value[i])

    return x_hat, p_hat
