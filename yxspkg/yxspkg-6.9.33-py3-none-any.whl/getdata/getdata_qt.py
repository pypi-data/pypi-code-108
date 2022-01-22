from yxspkg import songziviewer
import sys 
from PyQt5.QtWidgets import (QApplication,  QLabel,QWidget,QMessageBox,QDesktopWidget,QMenu,QAction,QTextEdit,
                            QHBoxLayout,QVBoxLayout,QPushButton,QFileDialog)
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import Qt,QPoint,QRect
class YButton(QPushButton):
    def __init__(self,d=None):
        super().__init__(d)
        # self.setStyleSheet('border:none')
    def setButton(self,I,pw,ph,objectname,position=None,callback = None):
        if I is not None:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(I))
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(pw , ph))
        self.setObjectName(objectname)
        if position is not None:self.setGeometry(QtCore.QRect(*position))
        self.clicked.connect(self.selfCallback)
        if callback is not None:self.callback = callback
    def selfCallback(self):
        self.change()
        self.callback(self)
    def change(self):
        text = self.text()
        if text.startswith('>>'):
            self.setText(text[2:])
        else:
            self.setText('>>'+text)

class GetData(QWidget):   #抓取数据gif
    def __init__(self,filename=None,NextButton = True,max_tool_width = 300):
        super().__init__()
        self.image_viewer = songziviewer.ImageViewer(parent_widget=self,name=None,NextButton=False,
            auto_detect=True)
        self.image_viewer.set_image_click_callback(self.get_pos)
        self.image_viewer.move(0,0)
        self.setAcceptDrops(True)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.image_viewer)
        self.tool_layout = QVBoxLayout()
        self.result_box = QTextEdit('X          Y\n')
        self.result_box.setMaximumWidth(max_tool_width)
        self.tool_layout.addWidget(self.result_box)
        self.main_layout.addLayout(self.tool_layout)
        self.setLayout(self.main_layout)
        #获取坐标
        self.origin_button = YButton('设置坐标')
        self.origin_button.setButton(None,None,None,None,callback = self.set_origin)
        self.data_button = YButton('抓取数据')
        self.data_button.setButton(None,None,None,None,callback = self.fetch_data)
        l = QHBoxLayout()
        l.addWidget(self.origin_button)
        l.addWidget(self.data_button)
        self.tool_layout.addLayout(l)


        #打开图片，保存数据
        self.open_button = YButton('打开')
        self.open_button.setButton(None,None,None,None,callback = self.fileOpen)
        self.save_button = YButton('保存')
        self.save_button.setButton(None,None,None,None,callback = self.fileSave)
        l = QHBoxLayout()
        l.addWidget(self.open_button)
        l.addWidget(self.save_button)
        self.tool_layout.addLayout(l)

        self.fetching_data = False
        self.setting_origin = False 
        #坐标系
        self.coordinate = dict()
        self.axis_points = list()
        self.axis_value  = [0,1,0,1]
        self.result_values = list()
        # self.after_open(filename)
        self.show()
        
    def set_origin(self,button):
        if not self.setting_origin:
            self.setting_origin = True 
            self.axis_points = list()
            self.coordinate = dict()
            self.image_viewer.label.drawElements['lines'] = list()
            print('start setting origin')
        else:
            self.setting_origin = False 
    def fetch_data(self,button):
        if not self.fetching_data:
            self.fetching_data = True
            print('start fetch data')
        else: 
            self.fetching_data = False 
    def convertValue(self,x,y):
        #转换为对应坐标系下的值
        origin = self.coordinate['Origin']
        unitx  = self.coordinate['UnitX']
        unity  = self.coordinate['UnitY']
        Xaxis  = self.coordinate['Xaxis']
        Yaxis  = self.coordinate['Yaxis']
        C_parallel_Y = -(x*Yaxis[0] + y*Yaxis[1])
        C_parallel_X = -(x*Xaxis[0] + y*Xaxis[1])
        xp = self.get_cross_point(Xaxis,(Yaxis[0],Yaxis[1],C_parallel_Y))
        yp = self.get_cross_point(Yaxis,(Xaxis[0],Xaxis[1],C_parallel_X))
        dx = ((xp[0]-origin[0])**2 + (xp[1] - origin[1])**2) ** 0.5
        dy = ((yp[0]-origin[0])**2 + (yp[1] - origin[1])**2) ** 0.5
        return dx/unitx, dy/unity
    def get_pos(self,pos):
        x,y = pos
        if self.fetching_data:
            self.image_viewer.label.drawElements['points'].append((x,y))
            value_x,value_y = self.convertValue(x,y)
            self.result_box.append('{:.9e},{:.9e}'.format(value_x,value_y))
            self.result_values.append((value_x,value_y))
            print(value_x,value_y)
        elif self.setting_origin:
            self.axis_points.append((x,y))
            
            if len(self.axis_points) %2 == 0:
                self.image_viewer.label.drawElements['points'].pop(-1)
                x1,y1 = self.axis_points[-2]
                x2,y2 = self.axis_points[-1]
                vx,vy = x2-x1,y2-y1 
                ydim,xdim = self.image_viewer.label.shape 
                l = ((xdim**2 + ydim**2) ** 0.5)/(vx**2+vy**2)**0.5
                xt2,yt2 = x1+vx*l,y1+vy*l 
                xt1,yt1 = x1-vx*l,y1-vy*l 
                self.image_viewer.label.drawElements['lines'].append(((xt1,yt1),(xt2,yt2)))
            else:
                self.image_viewer.label.drawElements['points'].append((x,y))
            
            if len(self.axis_points) == 4:
                Xaxis = self.get_a_lineABC(self.axis_points[0],self.axis_points[1])
                Yaxis = self.get_a_lineABC(self.axis_points[2],self.axis_points[3])
                Origin = self.get_cross_point(Xaxis,Yaxis)
                (x1,y1),(x2,y2) = self.axis_points[0],self.axis_points[1]
                dx = ((x1-x2)**2 + (y1-y2)**2)**0.5
                UnitX = dx / (self.axis_value[1]-self.axis_value[0])

                (x1,y1),(x2,y2) = self.axis_points[2],self.axis_points[3]
                dy = ((x1-x2)**2 + (y1-y2)**2)**0.5
                UnitY = dy / (self.axis_value[3]-self.axis_value[2]) 
                self.coordinate = { 'Xaxis':Xaxis,'Yaxis':Yaxis,'Origin':Origin,
                                    'UnitX':UnitX,'UnitY':UnitY}
                self.origin_button.change()
                self.setting_origin = False
    @staticmethod
    def get_a_lineABC(p1,p2):
        (x1,y1),(x2,y2) = p1,p2
        B = x1 - x2 
        A = y2 - y1 
        C = -y2*B - x2*A 
        return A,B,C
    @staticmethod
    def get_cross_point(L1,L2):
        (A1,B1,C1),(A2,B2,C2) = L1,L2
        t = A1*B2 - B1*A2 
        y = (A2*C1 - A1*C2) / t
        x = (C2*B1 - C1*B2) / t
        # assert abs(A1*x+B1*y+C1) < 1e-10
        # assert abs(A2*x+B2*y+C2) < 1e-10
        return x,y

    def dropEvent(self,e):
        if e.mimeData().hasUrls():
            files = [url.toLocalFile() for url in e.mimeData().urls()]
            self.after_open(files[0])
        else:
            e.ignore()
    def dragEnterEvent(self,e):
        e.accept()
    def fileOpen(self,button):
        fileName,_ = QFileDialog.getOpenFileName(self, "Open File")
        if fileName:
            self.after_open(fileName)
        button.change()
    def after_open(self,fileName):
        self.fileName = fileName 
        self.image_viewer.open_file(fileName)
        self.resize(self.width()-1,self.height())
    def fileSave(self,button):
        fileName,ext_f= QFileDialog.getSaveFileName(self, "Save File","","ascii (*.txt)")
        if fileName:
            print('save file')
            fp = open(fileName,'w')
            for i in self.result_values:
                fp.write('{:.12e} {:.12e}\n'.format(*i))
            fp.close()
        button.change()
            

def main(name=None):
    if len(sys.argv)==2:
        name=sys.argv[1]
    app = QApplication(sys.argv)
    Viewer = GetData(filename=name,NextButton=False)
    # app.installEventFilter(Viewer.image_viewer)
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()