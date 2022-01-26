
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel,QWidget,QApplication,QPushButton,QCheckBox,QHBoxLayout,QVBoxLayout
from PyQt5.QtGui import QImage,QPixmap,QCursor,QPainter,QColor
import sys
from PIL import Image
import numpy as np
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
class shadowLabel(QLabel):
    def __init__(self,panel,parent):
        super().__init__(panel)
        self.parent=parent
        self.setStyleSheet('QWidget{background-color:rgba(0,0,0,80)}')
class HCutLabel(QLabel):
    LineWidth=4
    LineLength=12
    def __init__(self,panel,parent):
        super().__init__(panel)
        self.parent=parent
        self.setStyleSheet('QWidget{background-color:rgb(0,0,0)}')
        self.resize(self.LineLength,self.LineWidth)
        self.pos_name=None
    def mousePressEvent(self,e):
        
        self.parent.ispressed=self.pos_name.split('_')[0]
        self.parent.wpos=QCursor.pos().x(),QCursor.pos().y()
    def mouseReleaseEvent(self,e):
        self.parent.ispressed=None
    def enterEvent(self,e):
        self.setStyleSheet('QWidget{background-color:rgb(90,90,90)}')
    def leaveEvent(self,e):
        self.setStyleSheet('QWidget{background-color:rgb(0,0,0)}')
class VCutLabel(HCutLabel):
    def __init__(self,panel,parent):
        super().__init__(panel,parent)
        self.resize(self.LineWidth,self.LineLength)
class radio_click_text_label(QLabel):
    def __init__(self,d):
        super().__init__(d)
        pass
class _ImageLabel(QLabel):
    def __init__(self,d,parent = None):
        super().__init__(d)
        self.parent = parent
        self.mask = None
        self.move_cut_widget = False
    def mouseMoveEvent(self,e):
        if self.mask is not None:
            h,w = self.img.shape[:2]
            w0,h0 = self.width(),self.height()
            rate = h0 / h
            x,y = int(e.x()//rate),int(e.y()//rate)
            for j in range(max(0,y-self.pen_width),min(self.img.shape[0], y+self.pen_width)):
                for i in range(max(0,x-self.pen_width),min(self.img.shape[1],x+self.pen_width)):
                    self.mask[j,i] = self.mask_type
            if self.mask_type == 0:
                mcolor = 0
            else:
                mcolor = (255,0,0)
            self.img[self.mask == self.mask_type] = mcolor
            q = QPixmap.fromImage(ndarry2qimage(self.img))
            self.setPixmap(q)
        elif self.move_cut_widget:
            x,y = QCursor.pos().x(),QCursor.pos().y()
            x0,y0 = self.mouse_pos0
            x1,y1,x2,y2 = self.cutpart0
            dx = x2-x1 
            dy = y2-y1
            x1 += x-x0
            y1 += y-y0
            self.parent.moveto(x1,y1,x1+dx,y1+dy,is_move=True)


    def mousePressEvent(self,e):
        self.move_cut_widget = True
        self.mouse_pos0=QCursor.pos().x(),QCursor.pos().y()
        self.cutpart0 = self.parent.cutpart
    def releasePressEvent(self,e):
        self.move_cut_widget = False
    def setGrab(self,m):
        if self.mask is None:
            p = self.pixmap()
            self.img = np.fromstring(Image.fromqpixmap(p).tobytes(),dtype = 'uint8').reshape((p.height(),p.width(),-1))
            self.img = self.img[:,:,:3]
            self.mask = self.img[:,:,0] * 0 + 3
            self.pen_width = self.img.shape[0] // 50
        self.mask_type = m

class CutImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cutpart=(20,20,70,70)
        self.panel = QWidget(self)
        self.imageLabel=_ImageLabel(self.panel,parent = self)
        self.imageLabel.setScaledContents(True)
        self.geometry_image=self.cutpart
        # self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.create_cut_tool(*self.cutpart)
        # self.resize(500,500)
        self.setMinimumSize(524,600)
        self.panel.resize(500,540)
        self.ispressed=None
        self.MinSize=(10,10)
        self.wpos=None  #鼠标初始位置
        self.moveto(*self.cutpart)
        self.ok_button=QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_event)
        self.ok_func=lambda x:None

        self.ratiobox=QCheckBox('应用于全部',self)

        self.ratiobox.stateChanged.connect(self.applyAll)
        self.ratiobox.toggle()  #设置默认值 self.apply_all=True

        self.keepbox=QCheckBox('1:1',self)
        self.keepbox.stateChanged.connect(self.checkRatio)
        self.keep_ratio=False
        self.cut_rate = None
        self.layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.layout.addWidget(self.panel)
        self.button_layout.addWidget(self.keepbox)
        self.button_layout.addWidget(self.ratiobox)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)
    def checkRatio(self,state):
        if state == QtCore.Qt.Checked:
            self.keep_ratio=True
            x1,y1,x2,y2=self.cutpart
            t=min(x2-x1,y2-y1)
            self.moveto(x1,y1,x1+t,y1+t)
        else:
            self.keep_ratio=False
        
    def resizeEvent(self,e):
        w,h = self.width(),self.height()
    def applyAll(self,state):
        if state == QtCore.Qt.Checked:
            self.apply_all=True
        else:
            self.apply_all=False
    def ok_event(self,e):
        self.destroy()
        x1,y1,x2,y2=self.cutpart
        self.ok_func({'img_geometry':self.geometry_image,'cutpart_geometry':(x1,y1,x2-x1,y2-y1),'isall':self.apply_all})
    def ok_connect(self,func):
        self.ok_func=func
    def create_cut_tool(self,x1=10,y1=10,x2=70,y2=70):
        self.shadow_up=shadowLabel(self.panel,self)
        self.shadow_bottom=shadowLabel(self.panel,self)
        self.shadow_right=shadowLabel(self.panel,self)
        self.shadow_left=shadowLabel(self.panel,self)

        self.up_left_label=HCutLabel(self.panel,self)
        self.up_left_label.pos_name='up_left'
        self.up_middle_label=HCutLabel(self.panel,self)
        self.up_middle_label.pos_name='up_middle'
        self.up_right_label=HCutLabel(self.panel,self)
        self.up_right_label.pos_name='up_right'

        self.bottom_left_label=HCutLabel(self.panel,self)
        self.bottom_left_label.pos_name='bottom_left'
        self.bottom_middle_label=HCutLabel(self.panel,self)
        self.bottom_middle_label.pos_name='bottom_middle'
        self.bottom_right_label=HCutLabel(self.panel,self)
        self.bottom_right_label.pos_name='bottom_right'

        self.right_up_label=VCutLabel(self.panel,self)
        self.right_middle_label=VCutLabel(self.panel,self)
        self.right_bottom_label=VCutLabel(self.panel,self)
        self.right_up_label.pos_name='right_up'
        self.right_middle_label.pos_name='right_middle'
        self.right_bottom_label.pos_name='right_bottom'

        self.left_up_label=VCutLabel(self.panel,self)
        self.left_middle_label=VCutLabel(self.panel,self)
        self.left_bottom_label=VCutLabel(self.panel,self)
        self.left_up_label.pos_name='left_up'
        self.left_middle_label.pos_name='left_middle'
        self.left_bottom_label.pos_name='left_bottom'

    def moveto(self,x1=10,y1=10,x2=70,y2=70,is_move=False):
        width=HCutLabel.LineWidth
        length=HCutLabel.LineLength
        window_length,window_width=self.panel.height(),self.panel.width()
        mx1,my1,mx2,my2=self.geometry_image
        mx2+=mx1
        my2+=my1

        def checkCutPart(x1,y1,x2,y2):
            if is_move:
                dx = x2 - x1 
                dy = y2 - y1
                if x1<mx1:
                    x1,x2 = mx1,mx1+dx
                if x2>mx2:
                    x1,x2 = mx2-dx,mx2 
                if y1<my1:
                    y1,y2 = my1,my1+dy 
                if y2>my2:
                    y1,y2 = my2-dy,my2 
                return x1,y1,x2,y2
            else:
                if x2-x1>self.MinSize[0] and y2-y1>self.MinSize[1] and x1>=mx1 and y1>=my1 and x2<=mx2 and y2<=my2:
                    return x1,y1,x2,y2 
                else:
                    return False
        t=checkCutPart(x1,y1,x2,y2)
        if t:
            self.cutpart=t
            x1,y1,x2,y2 = t
        else:
            return False
        self.up_left_label.move(x1-width,y1-width)
        self.up_middle_label.move((x2+x1-length)/2,y1-width)
        self.up_right_label.move(x2+width-length,y1-width)

        self.bottom_left_label.move(x1-width,y2)
        self.bottom_middle_label.move((x2+x1-length)/2,y2)
        self.bottom_right_label.move(x2+width-length,y2)

        self.right_up_label.move(x2,y1-width)
        self.right_middle_label.move(x2,(y2+y1-length)/2)
        self.right_bottom_label.move(x2,y2+width-length)

        self.left_up_label.move(x1-width,y1-width)
        self.left_middle_label.move(x1-width,(y2+y1-length)/2)
        self.left_bottom_label.move(x1-width,y2+width-length)

        self.shadow_up.setGeometry(0,0,window_width,y1)
        self.shadow_bottom.setGeometry(0,y2,window_width,window_length-y2)
        self.shadow_left.setGeometry(0,y1,x1,y2-y1)
        self.shadow_right.setGeometry(x2,y1,window_width-x2,y2-y1)
        self.sizeChangeEvent({'img_geometry':self.geometry_image,'cutpart_geometry':(x1,y1,x2-x1,y2-y1)})
        return True
    def mouseMoveEvent(self,e):

        if not self.ispressed:return
        wpos=self.wpos
        mpos=QCursor.pos().x(),QCursor.pos().y()
        x,y=mpos[0]-wpos[0],mpos[1]-wpos[1]
        x1,y1,x2,y2=self.cutpart
        if self.ispressed == 'left':
            x1+=x
            if self.keep_ratio:y2-=x
        elif self.ispressed == 'right':
            x2+=x
            if self.keep_ratio:y2+=x
        elif self.ispressed =='up':
            y1+=y
            if self.keep_ratio:x2-=y
        elif self.ispressed == 'bottom':
            y2+=y
            if self.keep_ratio:x2+=y
        
        t=self.moveto(x1,y1,x2,y2)
        if t:
            self.wpos=mpos
    def setImage(self,qimage,geometry=None,ratio=0.8):
        self.qimage = qimage
        self.imageLabel.setPixmap(QPixmap.fromImage(qimage))
        height_window,width_window=self.panel.height(),self.panel.width()
        height_image,width_image=qimage.height(),qimage.width()
        if geometry is None:
            height=height_window*ratio
            width=height/height_image*width_image
            if width>ratio*width_window:
                width=width_window*ratio
                height=width/width_image*height_image
            x=(width_window-width)/2
            y=(height_window-height)/2
            geometry=(int(x),int(y),int(width),int(height))
        self.geometry_image=geometry
        self.imageLabel.setGeometry(*geometry)
        self.moveto(geometry[0],geometry[1],geometry[0]+geometry[2],geometry[1]+geometry[3])

    def sizeChangeEvent(self,e):
        pass
class GrabImageWidget(CutImageWidget):
    def __init__(self,*d):
        super().__init__(*d)
        self.back_button = QPushButton('标记背景',self)
        self.front_button = QPushButton('标记前景',self)
        self.back_button.clicked.connect(self.set_back)
        self.front_button.clicked.connect(self.set_front)

        self.button_layout.insertWidget(0,self.back_button)
        self.button_layout.insertWidget(0,self.front_button)
        self.qp = QPainter()
        self.need_painted = False

        labels = [self.up_left_label,
        self.up_middle_label,
        self.up_right_label,

        self.bottom_left_label,
        self.bottom_middle_label,
        self.bottom_right_label,

        self.right_up_label,
        self.right_middle_label,
        self.right_bottom_label,

        self.left_up_label,
        self.left_middle_label,
        self.left_bottom_label]
        [i.hide() for i in labels]


    def set_back(self):
        self.imageLabel.setGrab(0)
    def set_front(self):
        self.imageLabel.setGrab(1)
    def ok_event(self,e):
        self.destroy()
        x1,y1,x2,y2=self.cutpart
        self.ok_func({'img_geometry':self.geometry_image,'cutpart_geometry':(x1,y1,x2-x1,y2-y1),'isall':self.apply_all,'mask':self.imageLabel.mask})

    
if __name__=='__main__':
    app=QApplication(sys.argv)
    tw=GrabImageWidget()
    tw.setImage(QImage('4.jpg'))
    tw.show()
    app.exec_()
    print(dir(QPixmap))