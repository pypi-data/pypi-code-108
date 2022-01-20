import os
import sys
import subprocess


class UtilsImg():
    def __init__(self):
        pass


    def saveImage(self, img_content, img_path):
        '''保存验证码图像'''
        if os.path.isfile(img_path):
            os.remove(img_path)
        fp = open(img_path, 'wb')
        fp.write(img_content)
        fp.close()


    def showImage(self, img_path):
        '''
        用于在不同OS显示图片(通常为验证码)
        (从皮卡丘那里白嫖来的~~)
        '''

        def show_img_use_PIL(img_path):
            "使用pillow库来打开图片"
            from PIL import Image
            img = Image.open(img_path)
            img.show()
            img.close()

        try:
            # 1. mac版 :
            if sys.platform.find('darwin') >= 0:
                "首选PIL. 当PIL报错时, 再选择subprocess"
                try:
                    show_img_use_PIL(img_path)
                except:
                    subprocess.call(['open', img_path])

            # 2. linux版
            elif sys.platform.find('linux') >= 0:
                "首选PIL. 当PIL报错时, 再选择subprocess"
                try:
                    show_img_use_PIL(img_path)
                except:
                    subprocess.call(['xdg-open', img_path])

            # 3. win版
            else:
                os.startfile(img_path)
        except:
            raise Exception("该系统无法打开图片, 请检查~\n")


    def removeImage(self, img_path):
        '''验证码验证完毕后关闭验证码并移除'''
        # 1. 关闭图片
        if sys.platform.find('darwin') >= 0:
            os.system("osascript -e 'quit app \"Preview\"'")
        # 2. 删除图片
        os.remove(img_path)



utils_img = UtilsImg()
