from DobotEDU.device import MagicBox
import DobotRPC
from DobotEDU import *
import requests
import json
import base64
import time


def test_shili():
    do = DobotEDU()
    assert do.__init__


def test_shili2():
    do = DobotEDU('222', '333')
    assert do.__init__


def test_shili3():
    dobotEdu = DobotEDU('yuejiang', 'YJ123456')
    assert dobotEdu.__init__


def test_tx():
    dobotEdu = DobotEDU('yuejiang', 'YJ123456')
    r = dobotEdu.nlp.topic('警方通报女游客无故推倒景区设施：由于个人生活发生重大变故导致情绪行为')
    # print(r)
    assert type(r) is str


def test_settoken():
    dobotEdu = DobotEDU()
    url = "https://dobotlab.dobot.cc/api/auth/login"
    headers = {"Content-Type": "application/json"}
    payload = {"account": "yuejiang", "password": "YJ123456"}
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    token = json.loads(r.content.decode())["data"]["token"]
    dobotEdu.token = token
    print(token)
    r = dobotEdu.nlp.topic('警方通报女游客无故推倒景区设施：由于个人生活发生重大变故导致情绪行为')
    # print(r)
    assert type(r) is str


def test_sy():
    dobotEdu = DobotEDU('yuejiang', 'YJ123456')
    r = dobotEdu.speech.synthesis('你好', 1)
    # print(r)
    assert type(r) is bytes


def ToBase64(file):
    with open(file, 'rb') as fileObj:
        image_data = fileObj.read()
        base64_data = base64.b64encode(image_data)
        return base64_data


def test_voice():
    do = DobotEDU('yuejiang', 'YJ123456')
    res = ToBase64('D:/gitttt/dobotedu/test/222.mp3')
    # print(res)
    res1 = do.speech.asr(res)
    # print(res1)
    assert type(res1) is str


def test_image():
    do = DobotEDU('yuejiang', 'YJ123456')
    res = ToBase64('D:/gitttt/dobotedu/test/4.jpg')
    # print(res)
    res2 = do.face.create_person(group_id="123",
                                 person_name="shua",
                                 person_id="333",
                                 image=res)
    assert res2 is not True
    # print(res2)


def test_magicbox():
    do = DobotEDU('yuejiang', 'YJ123456')
    res = do.magicbox.search_dobot()
    port = res[0]["portName"]
    do.magicbox.connect_dobot(port)
    do.m_lite.set_homecmd(port)
    do.magicbox.set_ptpwith_lcmd(port, 0)


def test_magicianlite():
    do = DobotEDU('yuyuyu', 'yuyu78YU')
    res = do.m_lite.search_dobot()
    print(res)
    port = res[0]["portName"]
    do.m_lite.connect_dobot(port)
    do.m_lite.set_homecmd(port)
    do.m_lite.set_jogjoint_params(velocity=10, acceleration=20)


def test_magicianhhh():
    do = DobotEDU('yuyuyu', 'yuyu78YU')
    res = do.magician.search_dobot()
    print(res)
    port = res[0]["portName"]
    do.magician.connect_dobot(port)
    do.magician.set_ptpcmd(port, 0, 200, 100, 0, 0)


def test_setporthhh():
    do = DobotEDU('yuyuyu', 'yuyu78YU')
    res = do.magician.search_dobot()
    print(res)
    port = "COM12"
    do.portname = port
    do.magician.connect_dobot()
    do.magician.set_homecmd()


def test_mbox():
    do = DobotEDU('yuyuyu', 'yuyu78YU')
    res = do.magicbox.search_dobot()
    print(res)
    port = res[0]["portName"]
    do.magicbox.connect_dobot(port)
    do.magicbox.set_ptpcmd(port, 0, 200, 100, 0, 0)


def test_portbox():
    do = DobotEDU('yuyuyu', 'yuyu78YU')
    res = do.magicbox.search_dobot()
    print(res)
    port = "COM12"
    do.portname = port
    do.magicbox.connect_dobot()
    do.magicbox.set_homecmd()


def test_setport():
    do = DobotEDU('yuyuyu', 'yuyu78YU')
    res = do.m_lite.search_dobot()
    print(res)
    port = "COM12"
    do.portname = port
    do.m_lite.connect_dobot()
    do.m_lite.set_homecmd()


def test_urlone():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    url = "https://dobotlab.dobot.cc"
    dobotEdu.url = url
    r = dobotEdu.speech.synthesis('你好', 1)
    print(r)


def test_urltwo():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    r = dobotEdu.speech.synthesis('你好', 1)
    print(r)


def test_urlthree():
    dobotEdu = DobotEDU("huang", "huangHUANG123")
    url = "https://dev.dobotlab.dobot.cc"
    dobotEdu.url = url
    r = dobotEdu.speech.synthesis('你好', 1)
    print(r)


# 测试重构后的wrapper函数get_portname
def test_getport():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.m_lite.search_dobot()
    # print(res)
    port = res[0]["portName"]
    do.m_lite.connect_dobot(port)
    do.m_lite.clear_allalarms_state(port)
    # do.m_lite.set_homecmd(port_name=port)
    do.m_lite.set_ptpcmd(port, ptp_mode=0, x=200, y=50, z=150, r=0)
    do.m_lite.set_ptpcmd(port, 0, 250, -20, 50, 0)
    do.m_lite.disconnect_dobot(port)
    # print('another method')
    # do.set_portname(port)  # 重新实例化，需要重连
    # print(999)
    # do.m_lite.connect_dobot()
    # do.m_lite.set_ptpcmd(0, 149, -20, 50, 0)
    # do.m_lite.set_ptpcmd(0, 200, 50, 150, r=0)


def test_boxm5():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    # do.magicbox.set_led_rgb(portname, 1, 2, 1, 200, 200)
    # do.magicbox.set_led_color(portname, 1, 2, "white", 10)
    # do.magicbox.set_led_state(portname, 1, 1, False)
    # do.magicbox.set_tts_volume(portname, 2, 2)
    # do.magicbox.set_tts_play(portname, 2, "加油")

    # do.magicbox.set_tts_tone(portname, 2, 5)
    # time.sleep(5)
    # do.magicbox.set_tts_cmd(portname, 2, 0)

    # do.magicbox.set_oled_text(portname, 4, "hehehe")
    # do.magicbox.set_oled_clear(portname, 4)
    # do.magicbox.set_oled_pos_text(portname, 4, 2, 1, "ttt")
    value = do.magicbox.get_color_result(portname, 3)
    print(value)


def test_cccccc():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    res = dobotEdu.robot.conversation(query="你好", session_id="")
    print(res)


def test_go():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    dobotEdu.set_portname("com2")
    dobotEdu.magiciango.set_rgb_light("LED_1", 0, 23, 23, 23, 23, 9)


def test_betago():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    dobotEdu.set_portname("com2")
    dobotEdu.beta_go.is_nearby([1, 2])


def test_card():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    # dobotEdu.set_portname("com2")
    image = ToBase64('test/images/idcards/111.jpg')
    card_side = "FRONT"
    res = dobotEdu.ocr.id_card(image, card_side)
    print(type(res))


def test_face_match():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    # dobotEdu.set_portname("com2")
    image1 = ToBase64('test/images/idcards/111.jpg')
    image2 = ToBase64('test/images/idcards/111.jpg')
    res = dobotEdu.face.match(image1, image2)
    print(res)


def test_ocr_base():
    dobotEdu = DobotEDU("yuyuyu", "yuyu78YU")
    # dobotEdu.set_portname("com2")
    image = ToBase64('C:/Users/Administrator/Pictures/idcards/111.jpg')
    res = dobotEdu.ocr.basic_general(image)
    print(res)


def test_set_converyor():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    a = do.magicbox.set_converyor(portname, magicbox.DUMMY, True, 250)
    print(a)


def test_set_port():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    a = do.magicbox.set_port(portname, 0, 1)
    print(a)


def test_rail():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    a = do.magicbox.get_rail_speed_ratio(portname)
    print(a)


def test_arm_speed():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    # a = do.m_lite.set_arm_speed_ratio(portname, 1, 50)
    # b = do.m_lite.get_arm_speed_ratio(portname, m_lite.JOG)
    # print("a, b", a, b)
    c = do.magician.set_arm_speed_ratio(portname, 1, 50)
    d = do.magician.get_arm_speed_ratio(portname, dobot_magician.CP)
    print("c, d:", c, d)


def test_alarm():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    a = do.m_lite.get_lost_step_result(portname)
    print(a)


def test_speech():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    text = "江行日已暮,何处可维舟。树里孤灯雨,风前一雁秋。离心缥缈水,魂梦到扬州。客散家声在,空江烟白萍。"
    res = do.speech.synthesis(text, 1)
    print(res)


def test_detect():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    image1 = ToBase64('test/images/idcards/111.jpg')
    res = do.face.detect(image1)
    print(res)


def test_search_ai():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    image1 = ToBase64('test/images/idcards/111.jpg')
    res = do.face.search([21], image1)
    print(res)


def test_ges_rrr():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    res = do.magicbox.search_dobot()
    print(res)
    portname = res[0]["portName"]
    do.magicbox.connect_dobot(portname)
    res = do.magicbox.get_ges_result(portname, 4)
    print(res)


def test_pyimageom():
    do = DobotEDU("yuyuyu", "yuyu78YU")
    image1 = ToBase64('test/images/idcards/3.jpg')
    res = do.pyimageom.set_background(str(image1))
    print(res)


# 2021/7/19-新增摇杆2接口，手势传感1接口


def test_joystick1():
    do = DobotEDU()
    res = do.magicbox.search_dobot()
    do.set_portname(port_name=res[0]["portName"])

    do.magicbox.connect_dobot()
    while 1:
        res = do.magicbox.get_ges_is_detected(port=6, ges=magicbox.UP)
        print(res)


def test_joystick2():
    do = DobotEDU()
    res = do.magicbox.search_dobot()
    do.set_portname(port_name=res[0]["portName"])

    do.magicbox.connect_dobot()
    while 1:
        res = do.magicbox.get_ges_result(port=6)
        print(res)


def test_joystick3():
    do = DobotEDU()
    res = do.magicbox.search_dobot()
    do.set_portname(port_name=res[0]["portName"])

    do.magicbox.connect_dobot()
    res = do.magicbox.is_joystick_button(port=2, index=magicbox.BTN_DOWN)
    print("down:", res)
    btn = do.magicbox.get_joystick_button(port=2)
    print(btn)
    pos = do.magicbox.get_joystick_pos(port=2)
    print(type(pos))


# 测试红外接口
def test_hongwai():
    do = DobotEDU()
    res = do.magicbox.search_dobot()
    do.set_portname(port_name=res[0]["portName"])

    do.magicbox.connect_dobot()
    while 1:
        res = do.magicbox.is_pir_detected(port=4)
        print("res:", res)


# 测试io12v电源输出
def test_power():
    do = DobotEDU()
    res = do.magicbox.search_dobot()
    do.set_portname(port_name=res[0]["portName"])

    do.magicbox.connect_dobot()
    do.magicbox.set_port(port=1, io_func=magicbox.DO)
    do.magicbox.set_io(1, 0)

    while 1:
        res = do.magicbox.get_do(port=1)
        print("res:", res)


# 测试int强转
def test_math():
    import math
    res = math.floor(9.56)
    res_num = int(res)
    print(res, res_num)


def test_red_blue():
    res = magicbox.search_dobot()
    port_name = res[0]["portName"]

    magicbox.connect_dobot(port_name)
    while 1:
        blue, red = magicbox.get_button_status(port_name, port=1)
        time.sleep(1)
        print(blue, red)