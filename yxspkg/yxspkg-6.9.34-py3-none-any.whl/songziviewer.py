from PyQt5.QtCore import  QTimer,Qt,QSize,QPoint,QEvent
from PyQt5.QtGui import QImage, QPixmap,QPainter,QFont,QColor,QPen,QCursor,QKeySequence,QIcon,QPalette
from PyQt5.QtWidgets import (QApplication,  QLabel,QWidget,QMessageBox,QDesktopWidget,QMenu,QAction)
from numpy import stack
import imageio
import sys
from os import path
from pathlib import Path
from PIL import Image
import numpy as np
import os
import time
import ctypes
from io import BytesIO
if sys.platform.startswith('win'):#为了使任务栏图标和标题栏图标一样，需要ctypes的设置
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    del ctypes
# imread=imageio.imread
__version__='1.1.5'
__author__='Blacksong'
def imread(obt):
    obt = Path(obt)
    if obt.suffix == '.jpxs':
        fp = open(obt,'rb')
        fp.read(2048)
        bimg = BytesIO()
        bimg.write(fp.read())
        return np.asarray(Image.open(bimg,mode="r"))
    else:
        return imageio.imread(obt)
class datarc(dict):
    def __init__(self,name):
        super().__init__()
        for i in open(name,'r'):
            s=i.strip()
            l=s.find('<')
            r=s.find('>')
            if l!=0 or r==-1:continue
            key=s[l+1:r].strip()
            value=s[r+1:].lstrip()

            self[key]=value
        if self['win_title'].strip() == 'True':
            self['win_title'] = True
        else:
            self['win_title'] = False
def setDefault():
    environ=os.environ
    if sys.platform.startswith('win'):
        home_path=path.join(environ['HOMEDRIVE'],environ['HOMEPATH'],'.songzgifrc')
    else:
        home_path=path.join(environ['HOME'],'.songzgifrc')
    if not path.exists(home_path):
        content='''<autoplay_interval>5
        <background_color>rgba(255,255,255,255)
<closebutton_background_color>rgba(0,0,0,0)
<title_background_color>rgba(0,0,0,0)
<border_background_color>rgba(0,0,0,0)
<win_title>True'''
        fp=open(home_path,'w')
        fp.write(content)
        fp.close()
    return datarc(home_path)
      
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


class YTitleLabel(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.parent=d[0]
        self.name_label=QLabel(self)
        self.name_label.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )
        self.name_label.hide()
        self.name_label.move(10,3)
    def mousePressEvent(self,e):
        if self.parent.resizeWindow:
            self.parent.mousePressEvent(e)
            return
        self.xt,self.yt=self.parent.x(),self.parent.y() #窗口最原始的位置
        self.x0,self.y0=self.xt+e.x(),self.yt+e.y()

    def mouseMoveEvent(self,e):
        if self.parent.resizeWindow:
            self.parent.mouseMoveEvent(e)
            return
        x,y=self.parent.x()+e.x(),self.parent.y()+e.y()
        dx,dy=x-self.x0,y-self.y0
        self.parent.move(self.xt+dx,self.yt+dy)
    def mouseDoubleClickEvent(self,e):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
    def enterEvent(self,e):
        if not self.parent.source_name:return
        name=path.basename(self.parent.source_name)
        self.name_label.setText(name)
        self.name_label.show()
    def leaveEvent(self,e):
        self.name_label.hide()
class YDesignButton(QLabel):
    position_dict={'center':Qt.AlignCenter,'left':Qt.AlignLeft,'hcenter':Qt.AlignHCenter,'vcenter':Qt.AlignVCenter,'justify':Qt.AlignJustify}
    def __init__(self,parent):
        super().__init__(parent)
        self.parent=parent
        self.clicked_connect_func=lambda :None
        self.setScaledContents(True)
        self.normal_qimg=None 
        self.focus_qimg=None
    def setNormalQimg(self,lines,color_background,color_text,img_size,width_pen=4):
        self.normal_qimg=self.getDrawLine(lines,color_background,color_text,img_size,width_pen)
        self.setPixmap(self.normal_qimg)
        if self.focus_qimg is None:
            self.focus_qimg = self.normal_qimg
    def setFocusQimg(self,lines,color_background,color_text,img_size,width_pen=4):
        self.focus_qimg=self.getDrawLine(lines,color_background,color_text,img_size,width_pen)
    def getDrawLine(self,lines,color_background,color_text,img_size,width_pen=4):
        qp=QPainter()
        img=QImage(img_size[0],img_size[1],QImage.Format_RGBA8888)
        img.fill(QColor(*color_background))
        qp.begin(img)
        qp.setPen(QPen(QColor(*color_text),width_pen,Qt.SolidLine))
 
        for i,j,m,n in lines:
            qp.drawLine(QPoint(i,j),QPoint(m,n))
        qp.end()
        qimg=QPixmap.fromImage(img)
        return qimg

    def mousePressEvent(self,e):
        self.clicked_connect_func()
    def enterEvent(self,e):
        self.setPixmap(self.focus_qimg)
    def leaveEvent(self,e):
        self.setPixmap(self.normal_qimg)

class NextPage(YDesignButton): #翻页按钮
    def __init__(self,*d):
        super().__init__(*d)
        self.clicked_connect_func=lambda a:None
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )
        l=[(10,50,70,50),(50,10,90,50),(90,50,50,90)]
        self.setNormalQimg(l,(0,0,0,0),(255,255,255,0),(100,100),10)
        self.setFocusQimg(l,(0,0,0,0),(255,255,255,0),(100,100),15)
    def clicked_connect(self,func):
        self.clicked_connect_func=func
    def mousePressEvent(self,e):
        self.clicked_connect_func(e)

class PrePage(YDesignButton): #翻页按钮
    def __init__(self,*d):
        super().__init__(*d)
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}' )
        self.clicked_connect_func=lambda a:None
        l=[(30,50,90,50),(50,10,10,50),(50,90,10,50)]
        self.setNormalQimg(l,(0,0,0,0),(255,255,255,0),(100,100),10)
        self.setFocusQimg(l,(0,0,0,0),(255,255,255,0),(100,100),15)
    def clicked_connect(self,func):
        self.clicked_connect_func=func
    def mousePressEvent(self,e):
        self.clicked_connect_func(e)
class BorderLine(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.setStyleSheet('QWidget{background-color:%s}' % default_value.get('border_background_color','rgba(0,0,0,100)'))
class YViewerLabel(QLabel):
    def __init__(self,*d):
        super().__init__(*d)
        self.parent=d[0]
        self.shape=(20,20)
        self.ndimg_s=None
        self.lefttop = None
        self.is_focus = False
        # 图片点击回调函数
        self.image_click_callback = None
        self.drawElements = {'lines':[],
                             'points':[]}
    def showimage(self,ndimg):
        self.ndimg_s=ndimg
        x,y,w,h=self.geometry_img
        ndimg=ndimg[y:y+h,x:x+w]
        qimg=ndarry2qimage(ndimg)
        self.setPixmap(QPixmap.fromImage(qimg))
    def paintEvent(self, e):########画图事件，每次update都会进入，想画啥根据注释进行,双击重画
        super().paintEvent(e)
        qp = QPainter()
        qp.begin(self)
        self.width_now = self.width()
        self.height_now = self.height()
        for key,val in self.drawElements.items():
            if val:
                if key == 'lines':
                    self.drawLines(qp,val) ######画线
                elif key =='points':
                    self.drawPoints(qp,val) #画点
        qp.end()
        
    def mousePressEvent(self,e):
        if e.button()==Qt.RightButton and self.parent.autoplay:
            self.start_time=time.time()
            self.single_right=True

        if self.parent.resizeWindow:
            self.parent.mousePressEvent(e)
            return
        # add callback
        if self.image_click_callback:
            pos=QCursor.pos()
            self.image_click_callback(self.parent.displayRGB(pos,fetch_only=True))
        self.lefttop=self.get_lefttop()
        self.dl=0,0
        self.xt,self.yt=self.x(),self.y() #图片
        self.x0,self.y0=self.xt+e.x(),self.yt+e.y()
        self.pw,self.ph=self.parent.width(),self.parent.height()
    def setImage(self,geometry_img=None,shape=None):
        self.geometry_img=geometry_img
        self.shape=shape
    def mouseMoveEvent(self,e):
        if self.parent.resizeWindow:
            self.parent.mouseMoveEvent(e)
            return
        x,y=self.x()+e.x(),self.y()+e.y()
        if x<0 or y<0 or x>self.pw or y>self.ph:return
        dx,dy=x-self.x0,y-self.y0
        self.move(self.xt+dx,self.yt+dy)
        self.dl=dx,dy
    def mouseDoubleClickEvent(self,e):
        self.single_right=False
        if e.button()==Qt.RightButton:
            self.parent.setAutoplay()
            return
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
    def mouseReleaseEvent(self,e):
        if e.button()==Qt.RightButton and self.parent.autoplay and self.single_right:
            self.end_time=time.time()
            if self.end_time-self.start_time>0.8:
                self.parent.change_autoplay(self.end_time-self.start_time)
        if self.lefttop is not None:
            self.update_geometry(self.lefttop,self.dl)
    def get_lefttop(self):  #
        factor=self.parent.factor
        end_geometry=self.geometry()
        gx,gy=end_geometry.x(),end_geometry.y()
        x_img,y_img=self.geometry_img[:2]
        ox=gx-x_img*factor 
        oy=gy-y_img*factor
        return ox,oy
    def update_geometry(self,origon=None,dl=None):
        if self.ndimg_s is None:return
        factor=self.parent.factor
        end_geometry=self.geometry()
        gx,gy,gw,gh=end_geometry.x(),end_geometry.y(),end_geometry.width(),end_geometry.height()
        w,h=self.parent.width(),self.parent.height()
        x_img,y_img,w_img,h_img=self.geometry_img
        x_new,y_new,w_new,h_new=gx,gy,gw,gh

        if gx<-w:
            dx=(-w-gx)/factor
            x_img+=dx
            x_new=-w
        if gy<-h:
            dy=(-h-gy)/factor
            y_img+=dy 
            y_new=-h

        if x_img>0 and gx>-w:
            dx=min((gx+w)/factor,x_img)
            x_img-=dx
            x_new-=dx*factor
        if y_img>0 and gy>-h:
            dx=min((gy+h)/factor,y_img)
            y_img-=dx
            y_new-=dx*factor

        w_new=w+w-x_new 
        h_new=h+h-y_new 
        w_img=min(w_new/factor,self.shape[1]-x_img)
        h_img=min(h_new/factor,self.shape[0]-y_img)
        self.geometry_img=int(x_img),int(y_img),int(w_img),int(h_img)
        x_img,y_img,w_img,h_img=self.geometry_img
        w_new=w_img*factor 
        h_new=h_img*factor
        x_new,y_new,w_new,h_new=int(x_new),int(y_new),int(w_new),int(h_new)
        ox=x_new-factor*x_img
        oy=y_new-factor*y_img 
        if origon:
            ox1,oy1=origon 
            dx,dy=dl 
            ox1,oy1=ox1+dx,oy1+dy
            dx,dy=ox-ox1,oy-oy1
            x_new-=dx 
            y_new-=dy
        self.setGeometry(int(x_new),int(y_new),int(w_new),int(h_new))
        self.showimage(self.ndimg_s)
        # print(x_new,y_new,w_new,h_new,'   '  , gx,gy,gw,gh)
    def enterEvent(self,event):
        self.is_focus = True
    def leaveEvent(self,event):
        self.is_focus = False
    def drawLines(self,qp,lines):
        qp.setPen(QPen(QColor(0,255,0),5,Qt.SolidLine))
        points = [self.convertImagePoint(i[0],i[1]) for l in lines for i in l]
        qp.drawLines(*points)
    def drawPoints(self,qp,points):
        qp.setPen(QPen(QColor(255,0,0),8,Qt.SolidLine))
        points = [self.convertImagePoint(x,y) for x,y in points]
        qp.drawPoints(*points)
    def convertImagePoint(self,x,y):
        px,py,pw,ph=self.geometry_img
        t = QPoint(round((x-px)*(self.width_now/pw)),round((y-py)*(self.height_now/ph)))
        return t
class ImageViewer(QWidget):   #预览gif
    gif_types=('.gif',)
    image_types=('.jpg','.jpeg','.ico','.bmp','.png','.tiff','.icns','.webp','.jpxs')
    def __init__(self,parent_widget = None,s='SongZ Viewer',name=None,NextButton = True,
                auto_detect = True):
        # auto_detect 是否自动检测鼠标位置及颜色
        self.auto_detect = auto_detect
        if parent_widget:
            super().__init__(parent_widget)
        else: 
            super().__init__()
        global default_value
        default_value=setDefault()  
        if default_value['win_title']:
            default_value['border_background_color']='rgba(0,0,0,0)'
            self.offset = 10000 #如果要显示win title 则将自身的title和closebutton移动相应的位置
            self.displayWindowTitle = True
        else:
            self.displayWindowTitle = False
            self.offset = 0
            self.setWindowFlags(Qt.FramelessWindowHint)#FramelessWindowHint
        print(default_value)
        self.setAcceptDrops(True)
        self.isMaximized_value=False
        self.timer=None
        self.autoplay=False
        self.resizeWindow=False

        self.border=0 #边界宽度
        self.label=YViewerLabel(self)
        self.label.setScaledContents(True)
        self.background_color=(255,255,255,255)
        # self.setStyleSheet('QWidget{background-color:%s}' % default_value['background_color'])
        
        background_color = default_value['background_color']
        nl = background_color.find('(')
        numbers = background_color[nl+1:-1].split(',')
        numbers = [int(i) for i in numbers]
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(*numbers))
        self.setPalette(palette)

        self.setMinimumSize(200,100)
        self.minimumSize_window=200,100
        self.title_height=26
        self.bottom_height=0

        
        
        self.first_window=True
        self.CloseButton=YDesignButton(self)
        self.CloseButton.setNormalQimg([(30,30,70,70),(30,70,70,30)],(0,0,0,0),(0,0,0,0),(100,100),4)
        self.CloseButton.setFocusQimg([(30,30,70,70),(30,70,70,30)],(255,0,0,255),(255,255,255),(100,100),4)
        self.CloseButton.setStyleSheet('QWidget{background-color:%s}' % default_value['closebutton_background_color'])
        self.Geometry_Desktop=QDesktopWidget().availableGeometry()
        self.max_image_height=self.Geometry_Desktop.height()

        self.RGBLabel = QLabel(self)
        self.RGBLabel.setStyleSheet("background:transparent")
        


        self.CloseButton.resize(self.title_height,self.title_height)
        self.CloseButton.clicked_connect_func=(self.close)
        #标题栏
        self.TitleLabel=YTitleLabel(self)
        self.TitleLabel.move(0,self.offset)
        self.TitleLabel.setStyleSheet('QWidget{background-color:%s}' % default_value['title_background_color'] )

        #翻页按钮
        if NextButton:
            self.nextbutton_size=(50,self.max_image_height)
        else:
            self.nextbutton_size=(0,0)
        self.nextbutton=NextPage(self)
        self.nextbutton.resize(*self.nextbutton_size)
        self.nextbutton.clicked_connect(self.next_image)
        self.prebutton=PrePage(self)
        self.prebutton.resize(*self.nextbutton_size)
        self.prebutton.clicked_connect(self.previous_image)

        self.factor=1
        self.factor_max=1000
        self.factor_min=0.04
        self.leftborder=BorderLine(self)
        self.rightborder=BorderLine(self)
        self.topborder=BorderLine(self)
        self.bottomborder=BorderLine(self)
        self.timer = None
        self.source_name=name
        if name:
            self.open_file(name)
            self.dir_images=self.get_images()
            self.dir_images_n=self.dir_images.index(path.abspath(name))
        else:
            self.dir_images=None
            self.resize(400,400)
            self.show()
        self.setMinimumSize(400,400)

        self.create_right_key_menu()

        if sys.platform.startswith('win'):
            try:
                icon_path = path.join(os.environ['HOMEDRIVE'] , os.environ['HOMEPATH'] , '.yxspkg','songzviewer','songzviewer.png')
                self.system_icon = QIcon(icon_path)
                self.setWindowIcon(self.system_icon)
            except:
                pass
    def dragEnterEvent(self,e):
        e.accept()
    def dropEvent(self,e):
        if e.mimeData().hasUrls():
            files = [url.toLocalFile() for url in e.mimeData().urls()]
            self.open_file(files[0])
        else:
            e.ignore()
    def set_image_click_callback(self,func):
        # 设置图片点击回调函数
        self.label.image_click_callback = func
    def create_right_key_menu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.customContextMenuRequested.connect(self.show_right_menu)  
  
        self.rightMenu = QMenu(self) 
        self.editAct = QAction("Edit with songzgif", self,  triggered=self.edit_with_songzgif)
        self.rightMenu.addAction(self.editAct) 

        self.rightMenu.addSeparator() 
    def edit_with_songzgif(self):
        from yxspkg.songzgif import gif
        self.gifMaker = gif.GifMaker(self.image_name)
    def show_right_menu(self, pos): # 重载弹出式菜单事件

        pos = QCursor.pos()
        pos.setX(pos.x()+2)
        pos.setY(pos.y()+2)
        self.rightMenu.exec_(pos)  
    def isMaximized(self):
        if sys.platform.startswith('darwin'):
            return self.isMaximized_value
        else:
            return super().isMaximized()   
    def showNormal(self):
        if sys.platform.startswith('darwin'):
            self.isMaximized_value=False
            self.setGeometry(self.Geometry_Normal)
        else:
            super().showNormal()
            self.setPosition()
    def showMaximized(self):
        if sys.platform.startswith('darwin'):
            self.isMaximized_value=True
            self.Geometry_Normal=self.geometry()
            self.setGeometry(self.Geometry_Desktop)
        else:
            super().showMaximized() 
            # w,h=self.width(),self.height()
            # t=self.get_base_factor(w,h,self.label.shape)
            # print(t,w,h)
            # self.scaleImage(t/self.factor)  
            self.setPosition()     
    def get_images(self):
        ps = Path(self.source_name)
        dname=ps.parent
        t=[]
        for i in self.image_types:
            t+=list(ps.parent.glob('*'+i))
        return [str(i) for i in t]
    def get_base_factor(self,w,h,shape):
        if shape[1]/shape[0]>w/h:
            t=w/shape[1]
        else:
            t=h/shape[0]
        return t
    def next_image(self,e):
        if not self.dir_images:return
        if e is True or e.button()==Qt.LeftButton:
            self.dir_images_n+=1
            if self.dir_images_n>=len(self.dir_images):
                self.dir_images_n=0
            self.open_file(self.dir_images[self.dir_images_n])
    def previous_image(self,e):
        if not self.dir_images:return
        if e is True or e.button()==Qt.LeftButton:
            self.dir_images_n-=1
            if self.dir_images_n<0:
                self.dir_images_n = len(self.dir_images)-1
            self.open_file(self.dir_images[self.dir_images_n])
    def open_file(self,name):
        self.image_name = name
        if name is not None:
            self.setWindowTitle(name.split(os.sep)[-1])
            try:
                if path.splitext(name)[-1].lower() in self.gif_types:
                    size = self.gif(name)
                else:
                    size = self.image(name)
                self.setWindowTitle(name.split(os.sep)[-1]+' [{}x{}]'.format(size[1],size[0]))
                return
            except Exception as e:
                self.setWindowTitle(name.split(os.sep)[-1])
                print(e,self.source_name)
                self.label.setText('cannot open file:{0}\nError:{1}'.format(self.source_name,e))
                if self.first_window:
                    self.resize(400,400)
                    self.move_center()
                    self.show()
                    self.first_window=False
    def move_center(self):
        w,h=self.width(),self.height()
        w0,h0=self.Geometry_Desktop.width(),self.Geometry_Desktop.height()
        x0,y0=self.Geometry_Desktop.x(),self.Geometry_Desktop.y()
        self.move(int((w0-w)/2+x0),int((h0-h)/2+y0))
    def gif(self,name):
        if isinstance(name,str):
            try:
                x=imageio.get_reader(name)
                meta=x.get_meta_data()
                fps=1000/meta.get('duration',None)
                jpgs=list(x)
                size=jpgs[0].shape
                size=size[1],size[0]
            except Exception as e:
                print('imageio',e)
                x=imageio.get_reader(name,'ffmpeg')
                meta=x.get_meta_data()
                fps=meta['fps']
                size=meta['size']
                jpgs=list(x)
        else:
            jpgs,fps,size=name
        self.preview((jpgs,fps,(size[1],size[0])))
        return size
    def image(self,name):
        s=imread(name)
        shape=s.shape 
        self.preview(([s],0.0001,shape[:2]))
        return shape[1],shape[0]
    def update_image(self):
        if self.nn>=len(self.jpgs):
            self.nn=0
        self.present_image=self.jpgs[self.nn]
        self.label.showimage(self.present_image)
        self.nn+=1

    def scaleImage(self,factor):
        tt=self.factor*factor
        if tt>self.factor_max or tt<self.factor_min:return
        self.factor_max=100000
     
        lefttop=self.label.get_lefttop()
        w,h=self.label.geometry_img[-2:]

        w0,h0=self.width()/2,self.height()/2

        dx=(w0-lefttop[0])*(1-factor)
        dy=(h0-lefttop[1])*(1-factor)
        
        self.factor*=factor
        self.label.resize(int(w*self.factor),int(h*self.factor))
        self.label.update_geometry(lefttop,(dx,dy))
        if self.factor*self.label.shape[0]<self.max_image_height:
            self.setPosition()
        x,y,w,h=self.label.geometry_img
        if w<30 or h<30:
            self.factor_max=max(self.factor,5)
    def setPosition(self):
        title_height=self.title_height
        bottom_height=self.bottom_height
        w,h=self.width(),self.height()
        self.CloseButton.move(w-title_height,self.offset)
        self.TitleLabel.resize(w-self.title_height,self.title_height)


        # h-=title_height+bottom_height
        w_label,h_label=self.label.width(),self.label.height()
        self.label.move(int((w-w_label)/2),int((h-h_label)/2))
        self.nextbutton.move(w-self.nextbutton_size[0]-5,title_height)
        self.prebutton.move(5,title_height)
        self.leftborder.resize(1,h)
        self.topborder.resize(w,1)
        self.rightborder.setGeometry(w-1,0,1,h)
        self.bottomborder.setGeometry(0,h-1,w,1)
        self.label.update_geometry()
        self.RGBLabel.setGeometry(0,h-20,300,20)
    def change_autoplay(self,t):
        self.setAutoplay()
        self.setAutoplay(t)
    def setAutoplay(self,t=None):
        if t is None:
            t=float(default_value['autoplay_interval'])
        if self.autoplay is True:
            self.autoplay=False
            self.timer_auto.stop()
        else:
            self.autoplay = True
            self.timer_auto=QTimer(self)
            self.timer_auto.timeout.connect(lambda :self.next_image(True))
            self.timer_auto.start(int(t*1000))
    def preview(self,parent):
        self.nn=0
        self.jpgs, self.fps ,shape  = parent
        self.label.setImage((0,0,shape[1],shape[0]),shape)
        if self.first_window:
            m=max(shape)
            t=1/max(1,m/self.max_image_height)
            self.resize(int(shape[1]*t+self.border*2),int(shape[0]*t+self.border*2+self.bottom_height))
            self.first_window=False
            self.move_center()
        else:
            w,h=self.width(),self.height()
            t=self.get_base_factor(w,h,shape)
            if self.timer:self.timer.stop()
        self.label.resize(int(shape[1]*t),int(shape[0]*t))
        self.factor=t
        self.setPosition()
        self.update_image()
        if self.fps != 0:
            self.timer=QTimer(self)
            self.timer.timeout.connect(self.update_image)
            t=int(1/self.fps*1000)
            self.timer.start(t)
        self.show()
    def isresizeMouse(self,x,y):

        x0,y0=self.x(),self.y()
        w0,h0=self.width(),self.height()
        width=4
        distance=8
        if x<x0+width and y0+h0-distance>y>y0+distance:#left
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resizeWindow='Left'
        elif x>x0+w0-width and y0+h0-distance>y>y0+distance:#right
            self.setCursor(QCursor(Qt.SizeHorCursor))
            self.resizeWindow='Right'
        elif y<y0+width and x0+w0-distance>x>x0+distance:#top
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resizeWindow='Top'
        elif y>y0+h0-width and x0+w0-distance>x>x0+distance:#bottom
            self.setCursor(QCursor(Qt.SizeVerCursor))
            self.resizeWindow='Bottom'
        elif x<x0+distance and y<y0+distance:#LeftTop
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
            self.resizeWindow='LeftTop'
        elif x>x0-distance+w0 and y>y0-distance+h0:#RightBottom
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
            self.resizeWindow='RightBottom'
        elif x<x0+distance and y>y0-distance+h0:#LeftBottom
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
            self.resizeWindow='LeftBottom'
        else:
            self.resizeWindow = False
            self.setCursor(QCursor(Qt.ArrowCursor))


    def runResizeWindow(self):
        pos=QCursor.pos()
        x,y=pos.x(),pos.y()
        if self.resizeWindow == 'Left':
            wt=self.w0+self.x0-x
            if self.minimumSize_window[0]>wt:return
            self.setGeometry(x,self.y0,wt,self.h0)
        elif self.resizeWindow == 'Right':
            wt=x-self.x0
            self.resize(wt,self.h0)
        elif self.resizeWindow == 'Bottom':
            ht=y-self.y0
            self.resize(self.w0,ht)
        elif self.resizeWindow == 'Top':
            ht=self.y0-y+self.h0
            if self.minimumSize_window[1]>ht:return
            self.setGeometry(self.x0,y,self.w0,ht)
        elif self.resizeWindow == 'RightBottom':
            wt,ht=x-self.x0,y-self.y0
            self.resize(wt,ht)
        elif self.resizeWindow == 'LeftTop':
            wt,ht=self.x0-x+self.w0,self.y0-y+self.h0
            if self.minimumSize_window[0]>wt:
                wt=self.minimumSize_window[0]
                x=self.x() 
            if self.minimumSize_window[1]>ht:
                ht=self.minimumSize_window[1]
                y=self.y()
            self.setGeometry(x,y,wt,ht)
        elif self.resizeWindow == 'LeftBottom':
            wt,ht=self.x0-x+self.w0,y-self.y0
            if self.minimumSize_window[0]>wt:
                wt=self.minimumSize_window[0]
                x=self.x() 
            if self.minimumSize_window[1]>ht:
                ht=self.minimumSize_window[1]
            self.setGeometry(x,self.y0,wt,ht)
    def mousePressEvent(self,e):
        if self.resizeWindow:
            self.x0,self.y0=self.x(),self.y()
            self.w0,self.h0=self.width(),self.height()
    def mouseMoveEvent(self,e):
        if self.resizeWindow:
            self.runResizeWindow()
    def resizeEvent(self,e):
        self.setPosition()
    def keyPressEvent(self,e):
        if e.matches(QKeySequence.MoveToPreviousLine):
            self.scaleImage(1/0.7)
        elif e.matches(QKeySequence.MoveToNextLine):
            self.scaleImage(0.7)
        elif e.matches(QKeySequence.MoveToPreviousChar):
            self.previous_image(True)
        elif e.matches(QKeySequence.MoveToNextChar):
            self.next_image(True)
    def wheelEvent(self,e):
        if self.first_window is True:
            return
        if e.angleDelta().y()>0:
            factor=1/0.8
        else:
            factor=0.8
        self.scaleImage(factor)
    # def get_xy_of_image(self,pos = None):
    #     if pos is None:
    #         pos = QCursor.pos()
    #     x,y = pos.x()-self.x()-self.label.x(),pos.y()-self.label.y()-self.geometry().y()
    #     label_x,label_y = self.label.width(),self.label.height()
    #     x0,y0,w,h=self.label.geometry_img
    #     dx, dy = int(x/label_x*w), int(y/label_y*h)
    #     x0+=dx
    #     y0+=dy
    #     return y0,x0
    def RGB2HSV(self,R,G,B):
        Cmax = max(R,G,B)
        Cmin = min(R,G,B)
        delta = Cmax - Cmin
        if delta == 0:
            H = 0
        elif Cmax == R:
            H = 60*((G-B)/delta)
            if H<0:
                H += 360
        elif Cmax == G:
            H = 60*((B-R)/delta + 2)
        else:
            H = 60*((R-G)/delta + 4)
        if Cmax == 0:
            S = 0
        else:
            S = delta / Cmax
        
        V = Cmax/255
        return H,S,V
    def displayRGB(self,pos,fetch_only = False):
        # fetch_only 只抓取位置，不显示
        if not fetch_only:
            if (not self.label.is_focus) or (not self.auto_detect):
                return
        parent = self.parent()
        px,py = pos.x(),pos.y()
        while parent:
            gpos = parent.geometry()
            px -= gpos.x()
            py -= gpos.y()
            parent = parent.parent()
        pos = self.pos()
        x,y = px-pos.x()-self.label.pos().x(),py-self.label.pos().y()-pos.y()
        label_x,label_y = self.label.width(),self.label.height()
        x0,y0,w,h=self.label.geometry_img
        if fetch_only:
            dx, dy = x/label_x*w, y/label_y*h
            return x0 + dx ,y0+dy
        else: 
            dx, dy = int(x/label_x*w), int(y/label_y*h)
        x0+=dx
        y0+=dy 
        try:
            RGB = self.present_image[y0,x0]
        except:
            RGB = 0,0,0
        # print(y0,x0,RGB,x,y)
        HSV = self.RGB2HSV(int(RGB[0]),int(RGB[1]),int(RGB[2]))
        if len(RGB)==3:
            s = "{},{} ,RGB:{},{},{}, HSV:{:3.0f}, {:.3f}, {:.3f}".format(y0,x0,*RGB,*HSV)
        else:
            s = "{},{} ,RGBA:{},{},{},{}, HSV:{:3.0f}, {:.3f}, {:.3f}".format(y0,x0,*RGB,*HSV)
        self.RGBLabel.setText(s)
    def eventFilter(self,source,event):
        t=event.type()
        if t == QEvent.MouseMove:
            if event.buttons() == Qt.NoButton:
                pos=QCursor.pos()
                # print(pos,event.globalPos())
                self.displayRGB(pos)
                # self.hide_button(pos.x()-self.x())
                if not self.isMaximized() and not self.displayWindowTitle:
                    self.isresizeMouse(pos.x(),pos.y())
        return super().eventFilter(source,event)

def main(name=None):
    
    if len(sys.argv)==2:
        name=sys.argv[1]
    app = QApplication(sys.argv)
    Viewer = ImageViewer(name=name,NextButton=True)
    tt = lambda x:print('ffff',x)
    Viewer.set_image_click_callback(tt)
    app.installEventFilter(Viewer)
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()