from DobotEDU import dobot_edu
import base64
import cv2
import time
import threading


def test_nopy():
    print(9999)

def test_main():
    dobot_edu.token = "ZjhiZjM3MjEtOGVkYS00NzM5LWI3ZDgtNjZlMGIyYjVmZjg5"

    print("initial...")
    print("main_thread00:", threading.main_thread())
    print("current_thread00:", threading.current_thread())
    text = "江行日已暮,何处可维舟。树里孤灯雨,风前一雁秋。离心缥缈水,魂梦到扬州。客散家声在,空江烟白萍。"
    print("waiting...input...")
    res = dobot_edu.speech.synthesis(text, 1)
    text = "嘻嘻嘻嘻嘻"
    result = dobot_edu.tmt.translation(text, source="zh", target="en")
    print(result)
    print("end...")
    # print(res)


def test_pyimage():
    dobot_edu.token = "NDIwYjZhNTUtYjA0Mi00MjQ0LTg0ZjAtYWQxMzU4ODAwY2Vh"

    def to_base64(file_name):  # 转化为Base64格式
        with open(file_name, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            return base64_data

    def get_image(file_name, timeout, port, flip=False):
        pic = dobot_edu.util.get_image(timeout, port, flip)
        cv2.imwrite(file_name, pic)
        base64_image = to_base64(file_name).decode("utf-8")
        return base64_image, pic

    # 背景照
    back_ground = get_image("D:/1.png", 5, 0)
    # 背景校准
    dobot_edu.pyimageom.set_background(back_ground[0])
    cv2.waitKey(0)
    size = int(input("请输入数据集的数量："))  # 数据集数量
    data_base = {}
    for j in range(size):
        # 弹窗拍照分割
        a = input("请输入数据集名称：")
        print(a)
        data_base[j] = a
        res = get_image("D:/1.png", 5, 0)
        print("要开始切拉。。。。")
        time.sleep(5)
        print("xiuxijieshu...")
        resq = dobot_edu.pyimageom.color_image_cut(res[0])
        print("color_image_cut: ", resq)
        # 显示分割结果
        if len(resq) == 0:
            print("没有可以切割的东西")
        else:
            for i in range(len(resq)):
                cv2.rectangle(res[1], (resq[i][2], resq[i][3]),
                              (resq[i][4], resq[i][5]), (0, 255, 0), 3)
                img = res[1].copy()
                dst = cv2.putText(res[1], str(i), (resq[i][0], resq[i][1]),
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255),
                                  4, 4)

        cv2.imshow("showImageResult", dst)
        cv2.waitKey(0)

        # 切割图片显示，输入格式0123,12,3

        # 训练失败，输入f
        a = input("你想要哪些照片加入数据集训练:")
        a_li = list(a)
        # a_li = ['0', '1', '2']
        # 把a转换成list,格式['0', '1', '2']
        # 存储切割后图片数据
        if a[0] == 'f':
            print("退出训练")
        else:
            cut_all = []
        if len(a_li) == 0:
            print("没有想要选择的照片")
        else:
            for k in range(len(a_li)):
                d = int(a_li[k])  # 选择了第几个矩形框
                # 将选择的矩形框内照片数据存取
                # 此处和形状切割不同，前端显示2,3,4,5，传到接口内的数据是6,7,8,9
                cut = img[resq[d][7]:resq[d][9], resq[d][6]:resq[d][8]]
                cv2.imwrite('D:/cut.jpg', cut)
                #cv2.imshow("cut image",cut)
                #cv2.waitKey(0)
                base64_data = to_base64('D:/cut.jpg').decode("utf-8")
                cut_all.append(base64_data)
            if len(cut_all) == 1:
                res = dobot_edu.pyimageom.color_image_classify([cut_all[0]],
                                                               [0], size, 2)
                print("color_image_classify: ", res)
            elif len(cut_all) == 0:
                print("没有想存储的照片")
            else:
                for m in range(len(cut_all)):
                    if m == 0 and j == 0:
                        a = dobot_edu.pyimageom.color_image_classify(
                            [cut_all[m]], [j], size, 0)
                        print(999, a)
                    elif m == len(cut_all) - 1 and j == size - 1:
                        dobot_edu.pyimageom.color_image_classify([cut_all[m]],
                                                                 [j], size, 2)
                    else:
                        dobot_edu.pyimageom.color_image_classify([cut_all[m]],
                                                                 [j], size, 1)

    # 拍照获取想要被识别照片
    print("训练结束，开始切割识别了")
    img_end = get_image('D:/2.png', timeout=5, port=0)

    # 分割
    resq = dobot_edu.pyimageom.color_image_cut(img_end[0])
    print(resq)
    # 显示分割结果
    if len(resq) == 0:
        print("没有可以识别的东西")
    else:
        for i in range(len(resq)):
            cv2.rectangle(img_end[1], (resq[i][2], resq[i][3]),
                          (resq[i][4], resq[i][5]), (0, 255, 0), 3)
            cut = img_end[1][resq[i][7]:resq[i][9], resq[i][6]:resq[i][8]]
            cv2.imwrite('D:/cut.jpg', cut)
            base64_data = to_base64('D:/cut.jpg').decode("utf-8")
            #img = img_end[1].copy()
            res = dobot_edu.pyimageom.color_image_group(base64_data)
            print("color_image_group:", res)
            dst = cv2.putText(img_end[1], data_base[int(res)],
                              (resq[i][0], resq[i][1]),
                              cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4,
                              4)
        cv2.imshow("显示结果", dst)
        cv2.waitKey(0)
        #cv2.imshow("showImageResult", dst)
        #cv2.waitKey(0)


def test_dobot():
    dobot_edu.token = "ZmE0YTNiZTEtNmZmMC00NGJmLWE3NTctM2QyNzRiZjU0YTE2"

    print("initial...")
    res = dobot_edu.magician.search_dobot()
    print(res)
    dobot_edu.magician.connect_dobot(res[0]["portName"])
    dobot_edu.set_portname(res[0]["portName"])
    while 1:
        dobot_edu.magician.set_ptpcmd(1, 247, 61, 14, 0)
        time.sleep(1)
        dobot_edu.magician.set_ptpcmd(1, 179, 116, 35, 0)
