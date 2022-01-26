import os
import sys
import tempfile
from io import StringIO
from os import path
import cv2
from pathlib import Path
import imageio
import numpy as np
import json
import yxspkg_pip as pip
from .. import songziviewer as yxspkg_songzviewer
from numpy import fromfile, frombuffer, hstack, stack
from PIL import Image, ImageFont
from PyQt5 import QtCore
from PyQt5.QtCore import QDir, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QColorDialog,
                             QDialog, QFileDialog, QFontDialog, QHBoxLayout,
                             QInputDialog, QLabel, QLineEdit, QMenu,
                             QMessageBox, QProgressBar, QPushButton,
                             QRadioButton, QScrollArea, QSizePolicy,
                             QVBoxLayout, QWidget)

import asyncio
from . import CutImageWidget

#sysplatform=sys.platform #mac:darwin
version='1.5.0'
software_name='SongZ GIF'
ffmpeg_file=None
cache_dir=tempfile.mkdtemp()
without_audio=False #默认采用添加音频
temp_nn=14 #标记 只增加不减小
global_ndarry_max=8*1024*1024*1024 #设置ndarray占用的最大内存
print('temp folder path:',cache_dir)


def resizeimg(img,size):
    shape=img.shape
    if shape[:2]==size:return img 
    if img.dtype!='uint8':
        img=img.astype('uint8')
    pimg=Image.fromarray(img)
    pimg=pimg.resize((size[1],size[0]))
    x=frombuffer(pimg.tobytes(),dtype='uint8')
    if len(shape)==2:
        x.shape=(size[0],size[1])
    else:
        x.shape=(size[0],size[1],-1)
    return x
def ndarryfile(s):
    if not isinstance(s,str):return s 
    _,shape,dtype=path.basename(s).split('_')
    shape=[int(i) for i in shape.split('.')]
    x=fromfile(s,dtype=dtype)
    x.shape=shape
    return x
def write_ndarryfile(s):
    global temp_nn
    shape,dtype=s.shape,s.dtype
    fname='{0}_{1}_{2}'.format(temp_nn,'.'.join([str(i) for i in shape]),dtype)
    p=path.join(cache_dir,fname)
    print(p)
    s.tofile(p)
    temp_nn+=1
    return p
def ndarry2qimage(npimg): #ndarry图片转化为qimage图片
    if npimg.dtype!='uint8':
        npimg=npimg.astype('uint8')
    shape=npimg.shape
    if len(shape)==3 and shape[2]==4:
        return QImage(npimg.tobytes(),shape[1],shape[0],shape[1]*shape[2],QImage.Format_RGBA8888)
    if len(shape)==2:
        npimg=stack((npimg,npimg,npimg),2)
        shape=npimg.shape
    s=QImage(npimg.tobytes(),shape[1],shape[0],shape[1]*shape[2],QImage.Format_RGB888)
    return s
class output_target:
    def __init__(self):
        self.text=''
    def write(self,s):
        self.text+=s
        if len(self.text)>1000:
            self.text=''
    def flush(self):
        pass
class ProgressBar(QWidget):
    def __init__(self, parent= None):
        super().__init__()
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Download ffmpeg')
        self.pbar = QProgressBar(self)
        self.line_t=QLineEdit(self)
        self.line_t.hide()
        self.line_t.setGeometry(30,90,200,30)
        layout=QHBoxLayout()
        layout.addWidget(self.pbar)
        self.timer = QTimer(self)
        self.step = 0
        self.timer.timeout.connect(self.setpro)
        self.timer.start(100)
        self.setLayout(layout)
    def setoutput(self,output):
        self.output=output
    def setpro(self):
        if self.step >=100:
            self.timer.stop()
            return
        t=self.output.text

        if len(t)>20:
            t=t[-20:]
            self.line_t.setText(t)
            n1=t.find('(')
            n2=t.find('%)')
            if n1!=-1 and n2!=-1:
                f=t[n1+1:n2]
                self.step=int(float(f))
        self.pbar.setValue(self.step)

class FFmpegDownloadThread(QThread):   
    trigger = pyqtSignal(tuple)
    def __int__(self):  
        super().__init__()  

    def setValue(self,bar,output):
        self.bar=bar
        self.output=output

    def run(self):
        t=sys.stdout
        sys.stdout=self.output
        while True:
            try:
                imageio.plugins.ffmpeg.download()
                break 
            except:
                pass
        sys.stdout=t

class TransformVideo(QThread):   
    trigger = pyqtSignal(tuple)
    def __int__(self):  
        super().__init__()  
    def setValue(self,filename):
        self.filename = filename

    def run(self):
        cap = cv2.VideoCapture(self.filename)
        fps = cap.get(5)
        temp_video_path = cache_dir+os.sep+'cache_cv2.mp4'
        videowriter = imageio.get_writer(temp_video_path,fps = fps)
        while cap.isOpened():
            _,img = cap.read()
            videowriter.append_data(img[:,:,::-1])
        videowriter.close()
        print('video transform complete')
        videoreader=imageio.get_reader(temp_video_path,'ffmpeg')
        self.trigger.emit((temp_video_path,False))


class YLineEdit(QLineEdit): #高度和宽度输入框
    def connect(self,func):
        self.callback=func
    def keyReleaseEvent(self,e):
        self.callback(self.text())

class setupWidget(QWidget):
    def __init__(self,parent):
        super().__init__()
        size=(350,100)
        self.resize(*size)
        self.setWindowTitle(software_name)
        layout=QVBoxLayout()
        self.setLayout(layout)
        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('当前版本号：'+version)
        font=QFont()
        font.setPixelSize(25)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QPushButton('检查更新')
        font=QFont()
        font.setPixelSize(25)
        l.setFont(font)
        l.clicked.connect(lambda:parent.checkupdate(self,True))
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

class aboutWidget(QWidget):  #about
    def __init__(self,*d):
        super().__init__(*d)
        size=(350,100)
        self.resize(*size)
        self.setWindowTitle(software_name)
        layout=QVBoxLayout()
        self.setLayout(layout)
        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel(software_name)
        font=QFont()
        font.setPixelSize(25)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('赠予我的Jesmine, ——Blacksong')
        font=QFont()
        font.setPixelSize(15)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('Copyright @ Blacksong')
        font=QFont()
        font.setPixelSize(15)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

        hlayout=QHBoxLayout()
        hlayout.addStretch() 
        l=QLabel('版本号：{version}'.format(version=version))
        font=QFont()
        font.setPixelSize(15)
        l.setFont(font)
        hlayout.addWidget(l)
        hlayout.addStretch() 
        layout.addLayout(hlayout)

class waitMessage(QWidget):
    def __init__(self,s="稍等..."):
        super().__init__()
        self.text=QLabel(self)
        self.text.setText(s)
        self.setWindowTitle('Runing... ')
        self.text.setGeometry(40,0,200,80)
        self.resize(160,80)
        self.show()
class SaveThread(QThread):   
    trigger = pyqtSignal(tuple)
    def __int__(self):
        super().__init__()
    def setValue(self,parent,filename):
        self.filename=filename
        self.parent=parent
        if ffmpeg_file is None:
            self.ffmpeg=imageio.plugins.ffmpeg.get_exe()
        else:
            self.ffmpeg=ffmpeg_file
        self.ffmpeg=self.ffmpeg.replace(' ','\\ ')
        parent.savedPath=path.dirname(filename)
    def generate_gif(self,jpgs,fps,size):
        kwargs_write = {'fps':fps} 
        # writer=imageio.get_writer(self.filename , fps=fps)
        tt = list()
        for i in jpgs:
            i=ndarryfile(i)
            if i.shape[:2]!=size:
                i=resizeimg(i,size)
            tt.append(i)
        #     writer.append_data(i)
        # writer.close()
        gif_mode = 'GIF'
        if self.parent.high_quality_gif:
            gif_mode = 'GIF-FI'
            kwargs_write['quantizer'] = 'nq'
        print('GIF mode:',gif_mode,kwargs_write)
        imageio.mimsave(self.filename,tt,gif_mode,**kwargs_write)
    def get_music_file(self,duration):
        if without_audio:return None
        music_file=self.parent.text_music_label.text().strip()
        if not music_file:return None
        music_file,start_time=music_file.split('|')
        outfile=path.join(cache_dir,'2323232323.aac')
        if sys.platform.startswith('darwin'):
            ffmpeg_cmd='{ffmpeg} -i "{infile}" -ss {start} -t  {duration} -y "{outfile}"'
        else:
            ffmpeg_cmd='{ffmpeg} -i "{infile}" -ss {start} -t  {duration} -acodec copy -y "{outfile}"'
        ffcmd=ffmpeg_cmd.format(ffmpeg=self.ffmpeg,infile=music_file,outfile=outfile,start=float(start_time),duration=float(duration))
        print(ffcmd)
        os.system(ffcmd)
        return outfile

    def generate_video(self,jpgs,fps,size):
        ffmpeg_params=['-s','{w}x{h}'.format(w=size[1],h=size[0])]
        writer=imageio.get_writer(self.filename , fps=fps,ffmpeg_params=ffmpeg_params)
        for i in jpgs:
            writer.append_data(ndarryfile(i))
        writer.close()
        music_file=self.get_music_file(len(jpgs)/fps)
        if music_file:
            ppname=path.join(path.dirname(self.filename),'.sdsd'+path.basename(self.filename))
            os.rename(self.filename,ppname)
            if sys.platform.startswith('darwin'):
                ffmpeg_cmd='{ffmpeg} -i "{video}" -i "{audio}" -y "{out}"'
            else:
                ffmpeg_cmd='{ffmpeg} -i "{video}" -i "{audio}" -c copy -y "{out}"'
            os.system(ffmpeg_cmd.format(ffmpeg=self.ffmpeg, video=ppname,audio=music_file,out=self.filename))
            os.remove(ppname)
            os.remove(music_file)
    def generate_image(self,size):
        outimg=ndarryfile(self.parent.board.current_image.ndimage)
        if outimg.shape[-1]==4 and path.splitext(self.filename)[1].lower() in ['.jpg','.jpeg']:
            outimg=outimg[:,:,:3]
        outimg=resizeimg(outimg,size)
        imageio.imwrite(self.filename,outimg)
    async def parallel_save_image(self,name,img):
        loop = asyncio.get_event_loop()
        future_ = loop.run_in_executor(None,imageio.imwrite,name,img)
        return await future_ 
    def generate_series_images(self,jpgs,size):
        
        fileName=self.filename[:-3]
        name,ext=path.splitext(fileName)
        max_n = 20 #最大同时存文件数目
        tasks = list()
        end_n = len(jpgs) - 1#最后一个图片的下标
        for n,i in enumerate(jpgs):
            img=ndarryfile(i)
            s='%06d' % (n,)
            if n % max_n+1 == max_n or n == end_n:
                tasks.append(self.parallel_save_image(name+s+ext,resizeimg(img,size)))
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(asyncio.wait(tasks))
                tasks = list()
            else:
                tasks.append(self.parallel_save_image(name+s+ext,resizeimg(img,size)))
    def run(self):
        fps=float(self.parent.text_fps_label.text())
        jpgs=self.parent.getNdImages()
        size=int(self.parent.text_h_label.text()),int(self.parent.text_w_label.text())
        try:
            if self.filename[-4:]=='.gif':
                self.generate_gif(jpgs,fps,size)
            elif path.splitext(self.filename)[1] in self.parent.image_files:
                self.generate_image(size)
            elif self.filename[-3:]=='%6d':
                self.generate_series_images(jpgs,size)
            else:
                self.generate_video(jpgs,fps,size)
        except Exception as e:
            self.trigger.emit((0,e)) 
            return
        self.trigger.emit((1,None)) 

class VideoReadThread(QThread):   
    trigger = pyqtSignal(tuple)
    def __int__(self):  
        super().__init__()  

    def setValue(self,videoreader):
        self.videoreader=videoreader

    def run(self):
        try:
            for i in self.videoreader:
                self.trigger.emit((i,))
        except:
            print('Reading warning!')
            return

class VideoCutter(QDialog):  #获取视频截取信息的输入对话框
    def __init__(self):
        super().__init__()
        self.info=None
        self.initUI()

    def initUI(self):
        h_p=20
        self.ts = QLabel("开始时间:", self)
        self.ts.move(10, h_p+2)
        self.ss = QLineEdit(self)
        self.ss.move(68, h_p)
        self.ss.resize(100,20)
        self.ss.setText('0:0:0')
        h_p+=25
        self.te = QLabel("结束时间:", self)
        self.te.move(10, h_p+2)
        self.se = QLineEdit(self)
        self.se.move(68, h_p)
        self.se.resize(100,20)
        self.se.setText('0:0:9')

        h_p+=25
        self.tf = QLabel("GIF帧率:", self)
        self.tf.move(10, h_p+2)
        self.sf = QLineEdit(self)
        self.sf.move(68, h_p)
        self.sf.resize(100,20)
        self.sf.setText('9')

        h_p+=35
        self.ok=QPushButton(self)
        self.ok.move(120,h_p)
        self.ok.setText('确定')
        self.ok.clicked.connect(self.accept)
        self.resize(200, 130)
        self.setWindowTitle("视频截取设置")
        self.show()

    def accept(self):
        start_time=[i.strip() for i in self.ss.text().split(':')]
        end_time=[i.strip() for i in self.se.text().split(':')]
        fps=self.sf.text().strip()
        try:
            start_time=float(start_time[0])*3600+float(start_time[1])*60+float(start_time[2])
            end_time=float(end_time[0])*3600+float(end_time[1])*60+float(end_time[2])
            fps=float(fps)
        except Exception as e:
            QMessageBox.information(self, "Input error",
                            "输入有误\n{0}".format(e))
            return
        self.info=start_time,end_time,fps
        super().accept()
    def get_info(self,duration,fps):
        if duration>10:
            duration=10
        self.se.setText('0:0:{0}'.format(str(duration)))
        self.sf.setText(str(fps))
        self.exec_()
        return self.info
class FontExample(QLabel):
    def setParent(self,parent):
        self.parent=parent
    def mousePressEvent(self,e):
        self.x0,self.y0=self.parent.position_input[0],self.parent.position_input[1]
        self.mx0,self.my0=e.pos().x(),e.pos().y()
    def mouseMoveEvent(self,e):
        self.parent.need_painted=True
        rotate=self.parent.rotate_input
        p_rate=self.parent.p_rate
        self.mx1,self.my1=e.pos().x(),e.pos().y()
        dx,dy=self.mx1-self.mx0,self.my1-self.my0
        dx*=-p_rate
        dy*=-p_rate

        # print(self.x0+dx,self.y0+dy)
        t=self.x0+dx,self.y0+dy
        self.parent.position_input=t
        self.parent.position_name.setText('%d,%d' % t)
class FontEditor(QDialog):  #获取字体设置信息
    def __init__(self,len_jpgs = 1):
        super().__init__()
        self.len_jpgs = len_jpgs
        self.info=None
        self.font_input=QFont()
        self.color_input=QColor(0,0,0)
        self.pointSize_default_font=self.font_input.pointSize()
        self.weight_default_font=50
        self.position_input=0,-30
        self.need_painted=True
        self.rotate_default_font=0
        self.rotate_input = self.rotate_default_font
        self.qp=QPainter()
        self.pen_weight=9
        
    def setColor(self):
        #options = QColorDialog.ColorDialogOptions(QFlag.QFlag(colorDialogOptionsWidget.value()))
        color = QColorDialog.getColor(Qt.green, self, "Select Color")
        if color.isValid():
            self.need_painted=True
            self.color_name.setText(color.name())
            self.color_input=color 
    def ndarrayonlabel(self,ndimg):
        qimg=ndarry2qimage(ndimg)
        qimg=qimg.scaledToHeight(ImageLabel.global_height)
        self.example.setPixmap(QPixmap.fromImage(qimg))
    def setFont(self):
        #options = QFontDialog.FontDialogOptions(QFlag(fontDialogOptionsWidget.value()))
        #font, ok = QFontDialog.getFont(ok, QFont(self.label_font.text()), self, "Select Font",options)
        font, ok = QFontDialog.getFont(self.font_input)
        if ok:
            self.need_painted=True
            self.font_input=font 
            self.size_name.setText(str(font.pointSize()))
            self.weight_name.setText(str(font.Weight()))
            self.font_label.setText(font.family())

    def paintEvent(self,e):
        if not self.need_painted:return
        self.need_painted=False
        qp=self.qp
        Qimg=self.Qimg.copy()
        qp.begin(Qimg)
        qp.rotate(self.rotate_input)
        qp.setFont(self.font_input)
        qp.setPen(self.color_input)
        shape=self.ndimg.shape
        qp.setWindow(self.position_input[0],self.position_input[1],shape[1],shape[0])
        qp.drawText(0,0,self.example_text)
        qp.end()
        Qimg=Qimg.scaledToHeight(ImageLabel.global_height)
        pimg=QPixmap.fromImage(Qimg)
        self.example.setPixmap(pimg)
    def checkRatio_define_text(self,state):
        if state == Qt.Checked:
            self.user_define_state=True 
            self.example_text="哈哈"
        else:
            self.user_define_state=False
            self.example_text=self.get_text_input()
        self.open_file_button.setEnabled(self.user_define_state)
    def open_txt(self):
        fileName,_ = QFileDialog.getOpenFileName(self, "Open File")
        if fileName:
            self.ss.setText(Path(fileName).name)
            self.user_define_json = fileName
    def initUI(self):
        l_content=QHBoxLayout()
        self.ts = QLabel("内容:")
        self.ss = QLineEdit()
        self.ss.setText('我能吞下玻璃而不伤害身体')
        self.open_file_button = QPushButton('打开')
        self.open_file_button.clicked.connect(self.open_txt)
        l_content.addWidget(self.ts)
        l_content.addWidget(self.ss)
        l_content.addWidget(self.open_file_button)

        l_define_text = QHBoxLayout()
        self.user_define_box = QCheckBox('给每一帧画面自定义内容')
        self.user_define_box.stateChanged.connect(self.checkRatio_define_text)
        self.checkRatio_define_text(False)
        self.json_info = QPushButton('Info')
        self.json_info.clicked.connect(
            lambda :QMessageBox.information(self, "Json Format",'''You should write a json file like this
#json content(if the key is missing, the default value will be used)
[{'text':'hello', 'color':'#ffffff', 'font':'Sans Serif', 'position':(20.4,20.4), rotate:90}, {...}]''')
            )
        l_define_text.addWidget(self.user_define_box)
        l_define_text.addWidget(self.json_info)

        l_font=QHBoxLayout()
        self.font = QLabel("字体:")
        self.font_label = QLineEdit('我能吞下玻璃而不伤身体')
        self.font_label.setReadOnly(True)
        self.font_selector=QPushButton('选择')
        self.font_selector.clicked.connect(self.setFont)
        l_font.addWidget(self.font )
        l_font.addWidget(self.font_label ,2)
        l_font.addWidget(self.font_selector)
        
        l_color=QHBoxLayout()
        self.color = QLabel("颜色:")
        self.color_name = QLineEdit()
        self.color_name.setReadOnly(True)
        self.color_selector=QPushButton('选择')
        self.color_selector.clicked.connect(self.setColor)
        l_color.addWidget(self.color)
        l_color.addWidget(self.color_name)
        l_color.addWidget(self.color_selector)
        l_size=QHBoxLayout()
        self.size = QLabel("大小:")
        self.size_name = QLineEdit()
        self.size_name.setText(str(self.pointSize_default_font))
        self.size_up=QPushButton('增大')
        self.size_down=QPushButton('减小')
        self.size_up.clicked.connect(lambda :self.__changeSize(1))
        self.size_down.clicked.connect(lambda :self.__changeSize(-1))
        l_size.addWidget(self.size)
        l_size.addWidget(self.size_name)
        l_size.addWidget(self.size_up)
        l_size.addWidget(self.size_down)

        l_weight=QHBoxLayout()
        self.weight = QLabel("粗细:")
        self.weight_name = QLineEdit()
        self.weight_name.setText(str(self.weight_default_font))
        self.weight_up=QPushButton('增大')
        self.weight_down=QPushButton('减小')
        self.weight_up.clicked.connect(lambda :self.__setFontWeight(10))
        self.weight_down.clicked.connect(lambda :self.__setFontWeight(-10))
        l_weight.addWidget(self.weight)
        l_weight.addWidget(self.weight_name)
        l_weight.addWidget(self.weight_up)
        l_weight.addWidget(self.weight_down)

        l_rotate=QHBoxLayout()
        self.rotate = QLabel("旋转:")
        self.rotate_name = QLineEdit('0')
        self.rotate_name.setText(str(self.rotate_default_font))
        self.rotate_up=QPushButton('顺时针')
        self.rotate_down=QPushButton('逆时针')
        self.rotate_up.clicked.connect(lambda :self.__setFontrotate(10))
        self.rotate_down.clicked.connect(lambda :self.__setFontrotate(-10))
        l_rotate.addWidget(self.rotate)
        l_rotate.addWidget(self.rotate_name)
        l_rotate.addWidget(self.rotate_up)
        l_rotate.addWidget(self.rotate_down)

        l_position=QHBoxLayout()
        self.position = QLabel("位置:")
        self.position_name = QLineEdit()
        self.position_name.setReadOnly(True)
        self.position_name.setText('0,0')
        l_position.addWidget(self.position)
        l_position.addWidget(self.position_name)

        
        self.ok=QPushButton()
        self.ok.setText('应用')
        self.ok.clicked.connect(self.accept)

        self.example=FontExample()
        self.example.setParent(self)
        self.ndarrayonlabel(self.ndimg)
        
        layout=QVBoxLayout()
        layout.addLayout(l_content)
        layout.addLayout(l_define_text)
        layout.addLayout(l_font)
        layout.addLayout(l_color)
        layout.addLayout(l_size)
        layout.addLayout(l_weight)
        layout.addLayout(l_rotate)
        layout.addLayout(l_position)
        layout.addStretch(1)
        layout.addWidget(self.ok)
        
        hlayout=QHBoxLayout()
        hlayout.addWidget(self.example)
        hlayout.addLayout(layout)
        
        
        self.setLayout(hlayout)

        self.setWindowTitle("文字设置")

        self.show()
    def get_text_input(self):
        if self.user_define_state:
            p = Path(self.user_define_json)
            if p.is_file():
                try:
                    texts = json.load(open(p,'r'))
                except Exception as e:
                    texts = None
                    QMessageBox.information(self, "File error",
                            "{0}\n{1}".format(p.name,e))
                    
        else:
            s=self.ss.text()
            texts = s.replace('\\n','\n')
        return texts
    def __setFontrotate(self,a):
        s=self.rotate_name.text()
        s=int(s)+a 
        self.rotate_name.setText(str(s))
        self.rotate_input=s 
        self.need_painted=True
    def __setFontWeight(self,a):
        self.need_painted=True
        s=self.weight_name.text()
        s=int(s)+a 
        self.weight_name.setText(str(s))
        self.font_input.setWeight(s)
        self.pen_weight=s

    def __changeSize(self,a):
        self.need_painted=True
        s=self.size_name.text()
        s=int(s)+a
        self.size_name.setText(str(s))
        self.font_input.setPointSize(s)

    def apply_input(self):
        pass
    def accept(self):#get the information of font
        texts = self.get_text_input()
        if not texts:return
        if self.user_define_state:
            texts = texts[:self.len_jpgs]
            if len(texts)<self.len_jpgs:
                n = self.len_jpgs - len(texts)
                texts.extend([{'text':''}]*n)
            t = self.font_input
            fonts = [i.get('font',t) for i in texts]
            list_texts = [i.get('text','') for i in texts]
            t = self.color_input
            colors = [i.get('color',t) for i in texts]
            t = self.position_input
            positions = [i.get('position',t) for i in texts]
            t = self.rotate_input
            rotates = [i.get('rotate',t) for i in texts]
            self.info = fonts, colors, positions, rotates, list_texts
        else:
            self.info=self.font_input,self.color_input,self.position_input,self.rotate_input, self.get_text_input()
        super().accept()
    def get_info(self,parent):
        self.parent=parent
        self.info=None
        self.ndimg=ndarryfile(parent.board.current_image.ndimage)
        self.Qimg=ndarry2qimage(self.ndimg)
        self.p_rate=self.ndimg.shape[0]/ImageLabel.global_height #实际尺寸与图片显示的尺寸的比值
        self.initUI()
        self.exec_()
        return self.info


class ImageLabel(QLabel):
    global_height=400
    def __init__(self,d):
        super().__init__(d)
        self.factor=1
        self.father=d
        self.setScaledContents(True)

        self.pages=QLabel(self)
        self.pages.move(0,0)
        self.pages.resize(70,20)
        self.father.current_image=self
        self.number = None

    def mousePressEvent(self,e):
        self.father.current_image=self
        self.father.isPressing=True
    def setImage(self,img):
        self.size=img.width(),img.height()
        img=img.scaledToHeight(self.global_height)
        self.setPixmap(QPixmap.fromImage(img))
        self.father.scaleImage(self)
    def setndimage(self,name): #Filename 可以是文件名 也可以是 ndarry
        self.father.ndarry_n+=name.size*name.itemsize
        if self.father.ndarry_n>self.father.ndarry_max:
            name=write_ndarryfile(name)
        self.ndimage=name

class ImageBoard(QWidget):
    def __init__(self,*d):
        super().__init__(*d)
        self.isMoving=False
        self.current_image=None
        self.need_init_set=True
        self.isPressing=False
        self.image_list=list()
        self.ndarry_n=0
        self.ndarry_max=global_ndarry_max

    def mouseMoveEvent(self,e):
        pass
    def mouseReleaseEvent(self,e):
        self.isPressing=False
        self.need_init_set=True
    def scaleImage(self,image):
        right=self.width()
        # print(right)
        w=image.pixmap().size().width()
        self.image_list.append([image,0,w,right]) #[图片label，编号,宽度，右边位置]
        image.move(right,0)
        right+=w
        self.resize(right,self.height())

class DrawImageWidget(QLabel): #用来绘制图片的Widget，不需要显示出来，后台运行
    def __init__(self,*d):
        super().__init__(*d)
        self.need_painted=False
        self.resize(2,2)
    def paintEvent(self,e):
        if not self.need_painted:
            return
        qp=QPainter()
        for i,img in enumerate(self.jpgs):
            img=ndarryfile(img)
            qimg=ndarry2qimage(img)
            qp.begin(qimg)
            qp.rotate(self.rotate_input[i])
            qp.setFont(self.font_input[i])
            qp.setPen(self.color_input[i])
            shape, position=img.shape, self.position_input[i]
            qp.setWindow(position[0],position[1],shape[1],shape[0])
            qp.drawText(0,0,self.text_input[i])
            qp.end()
            img=Image.fromqimage(qimg)
            img=frombuffer(img.tobytes(),dtype='uint8')
            img.shape=shape
            self.jpgs[i]=img
        self.need_painted=False
        self.finished_func()
    def setValue(self,font,color,position,rotate,text,jpgs):
        n = len(jpgs)
        if not isinstance(color,list):
            self.color_input=[color]*n
        else:
            self.color_input=color
        if not isinstance(font,list):
            self.font_input=[font] * n
        else:
            self.font_input=font
        if not isinstance(text,list):
            self.text_input=[text]*n
        else:
            self.text_input = text 
        if  not isinstance(position,list):
            self.position_input = [position]*n
        else:
            self.position_input=position 
        if not isinstance(rotate,list):
            self.rotate_input = [rotate]*n
        else:
            self.rotate_input = rotate 
        self.jpgs=jpgs
    def start_painting(self):
        self.need_painted=True
    def finished_connect(self,func):
        self.finished_func=func
class YScrollArea(QScrollArea):
    def __init__(self,*d):
        super().__init__(*d)
        self.bar=self.horizontalScrollBar()
    def wheelEvent(self,e):
        bar=self.bar
        if e.angleDelta().y()>0:
            m=-50
        else:m=50
        v=bar.value()
        bar.setValue(v+m)
    def enterEvent(self,e):
        self.entered=True
    def leaveEvent(self,e):
        self.entered=False

class GifMaker(QWidget):
    video_files=['.mp4','.mkv','.ts','.avi','.flv','.mov','.mpg','.m4v','.wmv']
    image_files=['.jpg','.jpeg','.bmp','.png','.ico','.icns','.tiff','.webp','.pcx']

    def __init__(self,img_init = None):
        super().__init__()
        
        self.videoclip=None
        self.setAcceptDrops(True)
        self.h=True
        self.interval=1
        self.savedPath=QDir.homePath()
        self.board = self.init_board()
        self.scrollArea=YScrollArea(self)
        width,height=820,400
        self.resize(width,height)
        self.scrollArea.setWidget(self.board)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.bar=self.scrollArea.horizontalScrollBar()

        vlayout = QVBoxLayout()
        self.outputlabel=QLabel('输出设置:')
        vlayout.addWidget(self.outputlabel)

        hlayout = QHBoxLayout()

        self.f_label=QLabel('帧数：')
        self.text_f_label=QLabel('0')

        hlayout.addWidget(self.f_label)
        hlayout.addWidget(self.text_f_label)

        vlayout.addLayout(hlayout)

        self.fps_label=QLabel('帧率：')
        self.text_fps_label=QLineEdit('10')

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.fps_label)
        hlayout2.addWidget(self.text_fps_label)

        vlayout.addLayout(hlayout2)

        self.h_label=QLabel('高度：')
        self.text_h_label=YLineEdit(self)
        self.text_h_label.connect(self.__check_height)
        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(self.h_label)
        hlayout3.addWidget(self.text_h_label)

        vlayout.addLayout(hlayout3)

        self.w_label=QLabel('宽度：')
        self.text_w_label=YLineEdit(self)
        self.text_w_label.connect(self.__check_width)
        hlayout4 = QHBoxLayout()
        hlayout4.addWidget(self.w_label)
        hlayout4.addWidget(self.text_w_label)

        vlayout.addLayout(hlayout4)

        self.ratiobox=QCheckBox('保持高宽比例',self)
        self.ratiobox.stateChanged.connect(self.checkRatio)
        self.ratiobox.toggle()  #设置默认值 self.ratio_state=True 
        vlayout.addWidget(self.ratiobox)
        
        self.cutButton=QPushButton('裁剪')
        self.cutButton.clicked.connect(self.cut)

        self.grabButton=QPushButton('前景提取')
        self.grabButton.clicked.connect(self.grab)

        self.textbutton=QPushButton('文字')
        self.textbutton.clicked.connect(self.__drawText)
        self.textbutton.setEnabled(False)
        
        self.gifibox=QCheckBox('高质量GIF输出',self)
        self.gifibox.stateChanged.connect(self.checkRatio_hgif)
        self.gifibox.toggle()
        self.openbutton=QPushButton('打开')
        self.openbutton.clicked.connect(self.open)
        self.savebutton=QPushButton('保存')

        self.savebutton.clicked.connect(self.save)
        self.savebutton.setEnabled(False)
        self.openbutton.setEnabled(False) #禁用 打开 按钮，等待所有模块加载完毕后启用

        self.musicbutton=QPushButton('音乐')
        self.musicbutton.clicked.connect(self.__insert_music)
        self.text_music_label=QLineEdit(self)

        self.previewbutton=QPushButton('预览')
        self.previewbutton.clicked.connect(self.preview)
        self.testbutton=QPushButton(self)
        self.testbutton.setText('测试')
        self.testbutton.clicked.connect(self.test)
        self.testbutton.hide()


        h1 = QHBoxLayout()
        h1.addWidget(self.cutButton)
        h1.addWidget(self.textbutton)
        vlayout.addLayout(h1)
        h2 = QHBoxLayout()
        h2.addWidget(self.grabButton)
        h2.addWidget(self.previewbutton)
        vlayout.addLayout(h2)
        h3 = QHBoxLayout()
        h3.addWidget(self.musicbutton)
        h3.addWidget(self.text_music_label)
        vlayout.addLayout(h3)

        vlayout.addStretch(1)
        save_layout = QVBoxLayout()
        h1 = QHBoxLayout()
        h1.addWidget(self.gifibox)
        h2 = QHBoxLayout()
        h2.addWidget(self.openbutton)
        h2.addWidget(self.savebutton)
        save_layout.addLayout(h1)
        save_layout.addLayout(h2)


        vlayout.addLayout(save_layout)

        self.hlayout = QHBoxLayout()
        self.hlayout.addWidget(self.scrollArea,10)
        self.hlayout.addLayout(vlayout,1)
        self.setLayout(self.hlayout)
        

        self.setWindowTitle(software_name)
        self.show()
        self.nn= 0 
        self.create_right_key_menu()

        self.update_sum_frames()
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.after_run)
        self.timer.start(30)
        if img_init is not None:
            if isinstance(img_init,str):
                self.open_files([img_init])
            elif isinstance(img_init,list):
                if isinstance(img_init[0],str):
                    self.open_files(img_init)
                else:
                    self.after_open(img_init)
            else:
                self.after_open([img_init])
        self.setMinimumSize(820,440)
    def after_run(self):#用于图形界面启动后导入模块以及检查更新

        self.openbutton.setEnabled(True) #模块加载完毕 启用打开按钮
        # self.checkupdate(self,False)  #开机自动检查更新
        self.timer.stop()
    def check_ffmpeg(self):
        try:
            ffmpeg=imageio.plugins.ffmpeg.get_exe()
        except:
            ffmpeg=None
        if not ffmpeg:
            reply = QMessageBox.question(self, "Download ffmpeg","你的系统中没有安装ffmpeg。点击确定自行安装ffmpeg，或者你也可以点击取消，自己安装ffmpeg（需要放到环境变量中）")
            if reply == QMessageBox.Yes:
                output=output_target()
                # output=open('out.txt','w+')
                self.probar=ProgressBar()
                self.probar.setoutput(output)
                self.probar.show()
                self.downloadThread=FFmpegDownloadThread()
                self.downloadThread.setValue(self.probar,output) 
                # self.downloadThread.trigger.connect(self.display_async)
                self.downloadThread.start()
                return True 
        else:
            return False
    def checkupdate(self,parent,display_already):
        need_ffmpeg=self.check_ffmpeg()
        if need_ffmpeg:return
        x=StringIO()
        self.waitmsg=waitMessage()
        out=sys.stdout
        sys.stdout=x
        out_argv=sys.argv
        sys.argv=['pip','install','yxspkg_songzgif','-U','--user']
        pip.main()
        sys.argv=out_argv
        sys.stdout=out 
        x.seek(0,0)
        t=x.read()
        self.waitmsg.close()
        if t.find('already up-to-date')!=-1:
            if display_already:
                QMessageBox.information(parent, "Update","已经是最新版本")
        else:
            QMessageBox.information(parent, "Update","已经更新到最新版本，重启后可用")

    def init_board(self):
        board=ImageBoard()
        board.resize(0,400)
        board.setMinimumSize(0,400)
        return board
    def closeEvent(self,e):
        try:
            for i in os.listdir(cache_dir):
                print('remove',i)
                os.remove(path.join(cache_dir,i))
            os.removedirs(cache_dir)
        except:
            pass
    def setEnabled_size(self,state):
        self.text_h_label.setEnabled(state)
        self.text_w_label.setEnabled(state)
        self.ratiobox.setEnabled(state)
        self.cutButton.setEnabled(state)
        self.grabButton.setEnabled(state)
        self.savebutton.setEnabled(state)
        self.text_fps_label.setEnabled(state)
        self.previewbutton.setEnabled(state)
        self.textbutton.setEnabled(state)
        self.gifibox.setEnabled(state)

    def create_right_key_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.customContextMenuRequested.connect(self.show_right_menu)  
  
        self.rightMenu = QMenu(self)  
        
        self.deleteCurrentAct = QAction("删除该帧", self,  triggered=self.__delete_image_current)
        self.rightMenu.addAction(self.deleteCurrentAct) 
        self.deleteBeforeAct = QAction("删除该帧及之前所有帧", self,  triggered=self.__delete_image_before)
        self.rightMenu.addAction(self.deleteBeforeAct) 
        self.deleteBehindAct = QAction("删除该处及之后所有帧", self,  triggered=self.__delete_image_behind)
        self.rightMenu.addAction(self.deleteBehindAct) 
        self.deleteSpecialAct = QAction("删除指定帧", self,  triggered=self.__delete_image_special)
        self.rightMenu.addAction(self.deleteSpecialAct) 
        self.deleteAllAct = QAction("删除所有帧", self, shortcut="delete",triggered=lambda:self.delete_image(0,-1))
        self.rightMenu.addAction(self.deleteAllAct) 
        
        self.rightMenu.addSeparator() 
        self.changefpsAct = QAction("改变帧率", self, triggered=self.__changefps)
        self.rightMenu.addAction(self.changefpsAct) 
        self.rightMenu.addSeparator() 
        self.insertimageAct = QAction("插入文件", self, triggered=self.__insertfile)
        self.rightMenu.addAction(self.insertimageAct) 
        self.reverseAct = QAction("逆序", self,triggered=self.__reverseimage)
        self.rightMenu.addAction(self.reverseAct)

        self.rotateAct = QAction("逆时针旋转90度", self,triggered=lambda :self.__rotate(90))
        self.rightMenu.addAction(self.rotateAct)

        self.rotate270Act = QAction("顺时针旋转90度", self,triggered=lambda :self.__rotate(270))
        self.rightMenu.addAction(self.rotate270Act)

        self.rotate180Act = QAction("旋转180度", self,triggered=lambda :self.__rotate(180))
        self.rightMenu.addAction(self.rotate180Act)

        self.rotate_1Act = QAction("左右镜像对称", self,triggered=lambda :self.__rotate(-1))
        self.rightMenu.addAction(self.rotate_1Act)

        self.rotate_2Act = QAction("上下镜像对称", self,triggered=lambda :self.__rotate(-2))
        self.rightMenu.addAction(self.rotate_2Act)

        self.mergeAct = QAction("合成一张图", self,triggered=self.__mergeimage)
        self.rightMenu.addAction(self.mergeAct)

        self.rightMenu.addSeparator() 
        self.saveimageAct = QAction("图片另存为", self, triggered=self.__saveimage)
        self.rightMenu.addAction(self.saveimageAct) 

        self.saveimageSeriesAct = QAction("导出图片序列", self, triggered=self.__saveimageSeries)
        self.rightMenu.addAction(self.saveimageSeriesAct) 

        self.rightMenu.addSeparator() 
        self.setupAct = QAction("设置", self,triggered=self.__setup)
        self.rightMenu.addAction(self.setupAct) 
        self.rightMenu.addSeparator() 
        self.setupAct = QAction("关于"+software_name, self, triggered=self.__about)
        self.rightMenu.addAction(self.setupAct) 
        self.right_act=[self.saveimageSeriesAct,self.changefpsAct ,self.mergeAct,self.rotate_2Act,self.rotate_1Act,self.rotate180Act,self.rotate270Act,self.rotateAct,self.reverseAct,self.deleteCurrentAct,self.deleteBeforeAct,self.deleteBehindAct,self.deleteAllAct,self.saveimageAct,self.insertimageAct,self.deleteSpecialAct]
    def __mergeimage(self):
        height=int(self.text_h_label.text())
        ndimages=self.getNdImages()
        shape0=ndarryfile(ndimages[0]).shape
        self.delete_image(0,-1)
        def ttf(a):
            i=ndarryfile(a)
            shape=i.shape
            if len(shape)==2:
                i=stack((i,i,i),2)
            elif len(shape)==3 and shape[2]==4:
                i=i[:,:,:3]
            else:
                pass
            return resizeimg(i,(height,int(i.shape[1]*height/i.shape[0])))
        img=hstack([ttf(i) for i in ndimages])
        self.after_open((img,))
    def __saveimageSeries(self):
        self.save(output_types="png Series Files (*.png)")
    def finished_response(self):
        
        jpgs=self.drawWidget.jpgs
        self.delete_image(0,-1)
        self.after_open(jpgs)
        self.drawWidget.hide()
    def __drawText(self):#draw text on image
        info = FontEditor(len_jpgs = len(self.board.image_list)).get_info(self)
        print(info)
        if info:
            #此处DrawImageWidget 中的对象只能写None,写self程序会崩溃，没找到原因
            self.drawWidget=DrawImageWidget(None)
            self.drawWidget.setValue(*info,self.getNdImages())
            self.drawWidget.start_painting()
            self.drawWidget.finished_connect(self.finished_response)
            self.drawWidget.show()
    def __changefps(self):
        fps0=float(self.text_fps_label.text())
        fps, ok = QInputDialog.getDouble(self, "QInputDialog.getDouble()", "输入帧率fps:", fps0, 0, 100, 2)
        if ok:
            jpgs=self.getNdImages()
            n=len(jpgs)*fps/fps0
            if n-int(n)>0.5:
                n2=int(n)+1
            else:
                n2=int(n)
            if n2==len(jpgs):return
            self.delete_image(0,len(jpgs))
            self.text_fps_label.setText(str(fps))
            for i in range(n2):
                t=int(i*fps0/fps)
                self.after_open((ndarryfile(jpgs[t]),))
    def __about(self):
        self._about=aboutWidget()
        self._about.show()
    def __rotate(self,angle=90):
        ndimages=self.getNdImages()
        self.delete_image(0,-1)
        op=self.after_open
        if angle==90:
            l=[op((ndarryfile(i)[:,::-1].swapaxes(1,0),)) for i in ndimages]
        elif angle==180:
            l=[op((ndarryfile(i)[::-1][:,::-1],)) for i in ndimages]
        elif angle==270:
            l=[op((ndarryfile(i)[::-1].swapaxes(1,0),)) for i in ndimages]
        elif angle==-2:
            l=[op((ndarryfile(i)[::-1],)) for i in ndimages]
        elif angle==-1:
            l=[op((ndarryfile(i)[:,::-1],)) for i in ndimages]
        else:
            return
    def __reverseimage(self):
        ndimages=self.getNdImages()
        ndimages.reverse()
        self.delete_image(0,-1)
        [self.after_open((ndarryfile(i),)) for i in ndimages]
    def __insertfile(self):#插入文件后覆盖之后的内容
        fileName,_ = QFileDialog.getOpenFileNames(self, "Open File",self.savedPath)
        if not fileName:return
        number=self.board.current_image.number
        self.delete_image(number-1,-1)
        self.open_files(fileName)
    def __insert_music(self):
        fileName,_ = QFileDialog.getOpenFileName(self, "Open File",self.savedPath)
        if not fileName:return
        self.text_music_label.setText(fileName+'|0.0')
    def __saveimage(self): #单独导出一张照片
        self.save(output_types="png Files (*.png);;jpg Files (*.jpg);;bmp Files (*.bmp);;All Files (*)")
    def checkRatio_hgif(self,state):
        if state == Qt.Checked:
            self.high_quality_gif = True 
        else:
            self.high_quality_gif = False
    def checkRatio(self,state):
        if state == Qt.Checked:
            h=self.text_h_label.text().strip()
            w=self.text_w_label.text().strip()
            if not h or not w:
                self.ratio_value=None  #图片高宽值（h,w)
            else:
                self.ratio_value=int(h)/int(w)
            self.ratio_state=True
        else:
            self.ratio_value=None
            self.ratio_state=False
    def __setup(self):
        self.setuplabel=setupWidget(self)
        self.setuplabel.show()
    def __check_height(self,s):#获取高度值
        if not s.isdigit() or self.ratio_state is False or self.ratio_value is None:return
        s=int(s)
        self.text_w_label.setText(str(int(s/self.ratio_value)))
    def __check_width(self,s):#获取宽度值
        if not s.isdigit() or self.ratio_state is False or self.ratio_value is None:return
        s=int(s)
        self.text_h_label.setText(str(int(s*self.ratio_value)))
    def __delete_image_current(self): #删除该帧及以前的图片
        n=self.board.current_image.number
        self.delete_image(n-1,n) 

    def __delete_image_behind(self): #删除该帧及以后的图片

        self.delete_image(self.board.current_image.number-1,-1)
    def __delete_image_special(self):
        start=self.board.current_image.number
        end=len(self.board.image_list)
        text,ok3 = QInputDialog.getText(self, "删除","起始帧-结束帧:",QLineEdit.Normal, "{0}-{1}".format(start,end))
        text=text.replace(' ','').split('-')
        if len(text)!=2 or not text[0].isdigit() or not text[1].isdigit():
            QMessageBox.information(self, software_name,"输入有误！！")
            return
        start,end=text
        start,end=int(start),int(end)
        if start>end or end>len(self.board.image_list):
            QMessageBox.information(self, software_name,"输入有误！！")
            return
        self.delete_image(start-1,end)

    def __delete_image_before(self): #删除该帧及以前的图片

        self.delete_image(0,self.board.current_image.number)

    def show_right_menu(self, pos): # 重载弹出式菜单事件
        if not self.scrollArea.entered:return
        if len(self.board.image_list)==0:
            for i in self.right_act:
                i.setEnabled(False)
        else:
            for i in self.right_act:
                i.setEnabled(True)
        pos = QCursor.pos()
        pos.setX(pos.x()+2)
        pos.setY(pos.y()+2)
        self.rightMenu.exec_(pos)  
    def delete_image(self,start,end):   #删除图片range(start,end)
        print(start,end)
        if end==-1:end=len(self.board.image_list)
        if end>len(self.board.image_list) or end<start:return False
        for i in self.board.image_list[start:end]:
            i[0].hide()
        if start==0:
            p_right=0
        else:
            p_right=sum(self.board.image_list[start-1][-2:])
        for i in self.board.image_list[end:]:
            image,number,width,position=i
            image.move(p_right,0)
            i[3]=p_right
            p_right+=width
        self.board.image_list=self.board.image_list[:start]+self.board.image_list[end:]
        self.board.resize(p_right,self.board.height())
        self.release_label_useless()
        self.update_sum_frames()

    def dropEvent(self,e):
        if e.mimeData().hasUrls():
            files = [url.toLocalFile() for url in e.mimeData().urls()]
            self.open_files(files)
        else:
            e.ignore()
    def release_label_useless(self):#释放多余的qlabel 减小内存占用
        v=self.scrollArea.bar.value()
        ndimages=self.getNdImages()
        self.board=self.init_board()
        self.scrollArea.setWidget(self.board)
        self.board.show()
        [self.after_open((ndarryfile(i),)) for i in ndimages]
        self.scrollArea.bar.setValue(v)

    def dragEnterEvent(self,e):
        e.accept()
    def getNdImages(self):
        return [i[0].ndimage for i in self.board.image_list]
    def save(self,testname=None,output_types="Gif Files (*.gif);;Mp4 Files (*.mp4);;Avi Files (*.avi);;All Files (*)"):
        def save_ok(a):
            self.waitmsg.close()
            if a[0]:
                QMessageBox.information(self,software_name,"成功保存了呦！")
            else:
                QMessageBox.information(self,software_name,"GG 保存出错了。\n{0}".format(a[1]))
        
        fileName,ext_f= QFileDialog.getSaveFileName(self, "Save Gif",self.savedPath,output_types)
        if not fileName:return
        if ext_f.find('Series')!=-1:
            fileName+='%6d'
        self.waitmsg=waitMessage('正在保存......')
        print(fileName)
        self.savethread=SaveThread()
        self.savethread.setValue(self,fileName)
        self.savethread.trigger.connect(save_ok)
        self.savethread.start()
    def update_sum_frames(self):  
        #此函数在图片帧数发生变化时会调用  很有用
        #更新帧数，图片左上角角标，图片编码( ImageLabel.number),
        self.text_f_label.setText(str(len(self.board.image_list)))
        for i,v in enumerate(self.board.image_list):
            t=i*self.interval+1
            v[0].pages.setText(str(t))
            v[0].number=t
            v[1]=t
        if not self.board.image_list: #保存按钮的开关设置
            self.ratio_value=None
            self.setEnabled_size(False)
            return
        self.setEnabled_size(True)

        image=self.board.image_list[0][0]
        if self.ratio_value is None and self.ratio_state is True:
            self.ratio_value=image.size[1]/image.size[0]
        self.text_h_label.setText(str(image.size[1]))
        self.text_w_label.setText(str(image.size[0]))

    def display_async(self,s):
        self.after_open(s)
    def editGif(self,filename):
        videoreader=imageio.get_reader(filename,'ffmpeg')
        fps=videoreader.get_meta_data()['fps']
        self.videoThread=VideoReadThread()
        self.videoThread.setValue(videoreader)
        self.videoThread.trigger.connect(self.display_async)
        self.videoThread.start()
        self.text_fps_label.setText('{0:.2f}'.format(fps))
    def video2gif(self,filename,Transform = True):
        try:
            videoreader=imageio.get_reader(filename,'ffmpeg')
        except:
            videoreader = None 
        if videoreader is None and Transform is True:
            self.transThread = TransformVideo()
            self.transThread.setValue(filename)
            self.transThread.trigger.connect(lambda x:self.video2gif(*x))
            self.transThread.start()
            return 
            # cap = cv2.VideoCapture(filename)
            # fps = cap.get(5)
            # temp_video_path = cache_dir+os.sep+'cache_cv2.mp4'
            # videowriter = imageio.get_writer(temp_video_path,fps = fps)
            # while cap.isOpened():
            #     img = cap.read()[:,:,::-1]
            #     videowriter.append_data(img)
            # videowriter.close()
            # videoreader=imageio.get_reader(temp_video_path,'ffmpeg')
        meta_data=videoreader.get_meta_data()
        duration=meta_data['duration']
        fps0=meta_data['fps']
        k=VideoCutter().get_info(duration,fps0)
        print(k)
        if k is None:return
        else:
            start,end,fps=k
            if end<start or fps<=0:return
        end=min(duration,end)
        def v_reader(reader,p_start,p_end,fps):
            for i in range(p_start,p_end):
                t=int(i/fps)
                yield reader.get_data(t)
        n=int((end-start)*fps)
        p_start=int(start*fps)
        self.videoThread=VideoReadThread()
        self.videoThread.setValue(v_reader(videoreader,p_start,p_start+n,fps/fps0))
        self.videoThread.trigger.connect(self.display_async)
        self.videoThread.start()
        self.text_fps_label.setText('{0:.2f}'.format(fps))
        self.text_music_label.setText(filename+'|'+str(start))
    @staticmethod
    def sort_filenames(files):
        names = [Path(i).name for i in files]
        name0 = names[0]
        istart = 0
        ibreak =False
        for i,s in enumerate(name0):
            if s.isdigit():
                for na in names:
                    if na[i] != s:
                        ibreak = True 
                        break 
                if ibreak:
                    istart = i-1
                    break
            else:
                istart = i
        iend = 0
        ibreak = False
        rname0 = reversed(name0)
        for j in range(1,len(name0)):
            i = -j 
            s = name0[i]
            if s.isdigit():
                for na in names:
                    if na[i] != s:
                        ibreak = True 
                        break 
                if ibreak:
                    iend = i+1
                    break
            else:
                iend = i
        try:
            files.sort(key=lambda x:float(Path(x).name[istart+1:iend]))
        except Exception as e:
            print(e)
    def open_files(self,files):# 对需要打开的文件进行甄别
        files=[i for i in files if path.isfile(i)]
        if not files: return
        self.savedPath=path.dirname(files[0])
        ext=path.splitext(files[0])[1]
        # print(ext)
        try:
            if len(files)==1:
                if ext.lower() in self.video_files:
                    print('Video')
                    self.video2gif(files[0])
                elif ext.lower()=='.gif':
                    self.editGif(files[0])
                elif ext.lower() in self.image_files:
                    t=imageio.imread(files[0])
                    self.after_open([t,])
                return
            else:
                self.waitmsg=waitMessage()
                self.sort_filenames(files)
                print(files)
                for i in files:
                    t=imageio.imread(i)
                    self.after_open([t,])
                self.waitmsg.close()
        except Exception as e:
            QMessageBox.information(self,software_name,"额,打开文件出错了,请重试。\n{0}".format(e))
    def open(self):#通过打开按钮来打开文件
        fileName,_ = QFileDialog.getOpenFileNames(self, "Open File",self.savedPath)
        self.open_files(fileName)
    def after_open(self,fileName): #文件已经打开，fileName是传输进来的ndarray图像列表 
        if fileName:
            for i in fileName:
                image=ndarry2qimage(i)
                self.noImage=False  
                imageLabel=ImageLabel(self.board)
                imageLabel.setImage(image)
                imageLabel.setndimage(i)
                imageLabel.show()
            self.update_sum_frames()
    def preview(self):
        jpgs=self.getNdImages()
        jpgs=[ndarryfile(i) for i in jpgs]
        fps=self.text_fps_label.text()
        fps=float(fps)
        print(fps)
        shape=jpgs[0].shape
        x=yxspkg_songzviewer.ImageViewer(None).gif((jpgs,fps,(shape[1],shape[0])))
        # x=GifPreview().preview(self)
    def cut(self):  #裁剪图片功能开始执行
        self.t=CutImageWidget.CutImageWidget()
        self.cutting_img=self.board.current_image.ndimage
        qimg=ndarry2qimage(self.cutting_img)
        self.t.setImage(qimg)
        self.t.ok_connect(self.get_cutsize)
        self.t.show()
    def grab(self):  #裁剪图片功能开始执行
        self.t=CutImageWidget.GrabImageWidget()
        self.cutting_img=self.board.current_image.ndimage
        qimg=ndarry2qimage(self.cutting_img)
        self.t.setImage(qimg)
        self.t.ok_connect(self.grab_pic)
        self.t.show()
    def grab_pic(self,info):
        mask = info['mask']
        if mask is None:
            return
        if not info['isall']:
            number=self.board.current_image.number
        else:
            number = -1

        npos=self.board.current_image.number
        self.update_grab(number,mask)
        self.board.current_image=self.board.image_list[npos-1][0]
        self.scrollArea.bar.setValue(self.board.image_list[npos-1][3])
    
    def grab_image_run(self,img,mask,bgdModel=None,fgdModel = None):
        if img.shape[-1]==4:
            img = img[:,:,:3]
        img = img[:,:,::-1]
        if not bgdModel:
            bgdModel = np.zeros((1,65),np.float64)
        if not fgdModel:
            fgdModel = np.zeros((1,65),np.float64)
        cv2.grabCut(img,mask,None,bgdModel,fgdModel,6,cv2.GC_INIT_WITH_MASK)
        mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
        img = img*mask2[:,:,np.newaxis]
        img = img[:,:,::-1]
        mask2*=255
        img = np.dstack((img,mask2[:,:,None]))
        return img

    def update_grab(self,number,mask):
        t=self.getNdImages()
        self.delete_image(0,-1)
        print('sddddddd',number)
        for i,img in enumerate(t):
            img=ndarryfile(img)
            if i==number-1 or number==-1:
                if mask.shape == img.shape[:2]:
                    img = self.grab_image_run(img,mask)
            self.after_open((img,))

    def update_cut(self,number):
        x1,y1,x2,y2=self.keep_size
        t=self.getNdImages()
        self.delete_image(0,-1)
        for i,img in enumerate(t):
            img=ndarryfile(img)
            if i==number-1 or number == -1:
                self.after_open((img[y1:y2,x1:x2],))
            else:
                self.after_open((img,))
    def get_cutsize(self,info):  #获取到裁剪后图片的大小
        img_geometry=info['img_geometry']
        if not info['isall']:
            number=self.board.current_image.number
        else:
            number=-1
        cutpart_geometry=info['cutpart_geometry']
        if img_geometry==cutpart_geometry:return
        x1,y1,w1,h1=img_geometry
        x2,y2,w2,h2=cutpart_geometry
        h,w=self.cutting_img.shape[:2]

        x2-=x1
        y2-=y1
        x1,y1=0,0

        x=x2/w1
        y=y2/h1 
        xx=x+w2/w1
        yy=y+h2/h1

        x,y,xx,yy=int(x*w),int(y*h),int(xx*w),int(yy*h)
        self.keep_size=x,y,xx,yy
        npos=self.board.current_image.number
        self.update_cut(number)
        self.board.current_image=self.board.image_list[npos-1][0]
        self.scrollArea.bar.setValue(self.board.image_list[npos-1][3])

    def test(self):  #测试按钮
        print(self.board.current_image.number)
def main(img = None):

    app = QApplication(sys.argv)
    gifMaker = GifMaker(img)
    sys.exit(app.exec_())
    return
if __name__ == '__main__':
    main(img = None)
    # print(dir(ImageFont))
    # s=ImageFont.truetype('黑体.ttf',23)
    # fname='4.jpg'
    # g=imageio.imread(fname)
    # font=QFont()
    # qp=QPainter()
    # qp.setFont(font)
    # x=TextOnImage(g,qp,(0,0),'haha')
    # imageio.imwrite(x,'sd.jpg')

    
    # print(g.shape)
    # qimage2ndarry(s)
    # print(dir(QImage))
