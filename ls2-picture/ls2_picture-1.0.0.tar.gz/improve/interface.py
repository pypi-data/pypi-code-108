import os
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from abc import ABC, abstractmethod
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import  calibration 

#import main_paras

import define
#from macro import * 
from algorithm import nothing, gauss, contrast, meanBlur,normalize, stretch, simplest_cb, his_equl_c_1,\
                his_equl_c_2, custom_blur, gray, he_ycrcb, clahe, target, bilateral, edsr, detection, clh_dtc
print(cv2.__version__)

default = 200
class _Improve(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_Improve, self).__init__(parent)
        self.algs = [nothing, gauss, contrast, meanBlur, normalize, stretch, simplest_cb, his_equl_c_1, bilateral, custom_blur, clh_dtc, he_ycrcb, detection,clahe, target]
        loadUi(os.path.join(currentdir,'improve.ui'),self)
        self.bar_list=self.centralwidget.findChildren(QtWidgets.QScrollBar)
        self.value_list=self.centralwidget.findChildren(QtWidgets.QLabel)
        self.algorithm = self.algs[0]
        self.img = []
        self.original_img=[]

        self.validation = False
        self.image_file_name=''
        self.workingPath =''

        self.file_list =[]
        self.file_index=0
        self.config()

    def setDefault(self):
        default_value = self.algorithm.defaultVaules()
        print(default_value)
        for i in range(len(self.bar_list)):
            if i in range(len(default_value)):
                self.bar_list[i].setRange(0,400)
                self.bar_list[i].setValue(default)
                self.value_list[i].setText(str(default_value[i]))
                self.bar_list[i].show()
                self.value_list[i].show()
            else:
                self.bar_list[i].hide()
                self.value_list[i].hide()
        self.repaint()

    def config(self):
        try:
            self.open.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.open.clicked.connect(self.open_hook)

            self.prev.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.prev.clicked.connect(self.prev_hook)
            self.next.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.next.clicked.connect(self.next_hook)
            
            self.send.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.send.clicked.connect(self.send_hook)
            self.save.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.save.clicked.connect(self.save_hook)
            self.restore.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.restore.clicked.connect(self.restore_hook)

            self.validate.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.validate.clicked.connect(self.validate_hook)

            self.off_line.clicked.connect(self.off_line_hook)
            
            self.buttonGroup.buttonClicked.connect(self.group_hook)
            for i in range(len(self.buttonGroup.buttons())):
                self.buttonGroup.setId(self.buttonGroup.buttons()[i],i)
                if i in range(len(self.algs)):
                    self.buttonGroup.buttons()[i].setText(self.algs[i].getName())
                else:
                    self.buttonGroup.buttons()[i].hide()
            self.buttonGroup.buttons()[0].setChecked(True)

            self.setDefault()
            for i in range(len(self.bar_list)):
                self.bar_list[i].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.bar_list[i].valueChanged.connect(self.value_changed)
            
        except Exception as error:
            print('config',error)

    def set_algorithm(self, alg):
        self.algorithm = alg
        
    def showNew(self,index=None,difference=None):
        #cv2.destroyAllWindows()
        try:
            if(self.img !=[]):
                #print(self.img, index, difference)
            
                newImg, new_value = self.algorithm.adjust(self.original_img, self.img, index, difference, chart = True)
                #print('result', index, new_value)
                if index!=None and new_value!=None:
                    self.value_list[index].setText(str(new_value))
                #cv2.destroyAllWindows()
                #horizontalStack = np.concatenate((self.img, self.newImg), axis=1)
                cv2.imshow("Original", self.img)
               
                for i in range(len(newImg)):
                    if isinstance(newImg[i], str):
                        print(newImg[i])
                    else:
                        cv2.imshow("Modified"+str(i), newImg[i])

##                mean, std = cv2.meanStdDev(self.img)
##                print('original mean std', mean, std)
##                mean, std = cv2.meanStdDev(self.newImg[0])
##                print('new mean std', mean, std)
                cv2.waitKey(1)
                #print('show')
            else:
                print('slelect image file first')
        except Exception as e:
            print(e)
        

    def value_changed(self, value):
        try:
            index = self.bar_list.index(self.sender())
            print('index',index,value)
            #print(self.img)
            self.showNew(index, value-default)


        except Exception as error:
            print('value_changed',error)

    def open_file(self):
        if self.validation:
            print(self.image_file_name)
            self.original_img = cv2.imread(self.image_file_name)
            self.img = calibration.crop_rotate(self.original_img)
            self.showNew()
            return 


        
        if self.workingPath != '':
            print(self.image_file_name)
            self.original_img = cv2.imread(os.path.join(self.workingPath,self.image_file_name))
            self.img = calibration.crop_rotate(self.original_img)
            self.showNew()
        else:
            print('No working folder and file')
        
    def open_hook(self):
        try:
            options = QtWidgets.QFileDialog.Options()
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Jpg Files (*.jpg; *.png)", options=options)
            if fileName:
                try:
                    
                    self.validation = False
                    self.image_file_name= os.path.basename(fileName)
                    self.workingPath = os.path.dirname(fileName)
                    self.file_list=[x for x in os.listdir(self.workingPath) if os.path.splitext(x)[1] in ('.jpg', '.png')]
                    self.file_index= self.file_list.index(self.image_file_name)
                    #print(self.file_list, self.file_index)

                    
                    
                except Exception as e:
                    print(e)
                    self.img=[]
                    self.image_file_name=''
                    self.file_list=[]
                    self.file_index=0
                    self.workingPath=[]
                self.open_file()
                

        except Exception as error:
            print(error)

    def next_hook(self):
        try:
            if self.file_list!=[]:
                self.file_index = (self.file_index + 1)%len(self.file_list)
                self.image_file_name = self.file_list[self.file_index]
                self.open_file()
        except Exception as error:
            
            print(error)

    def prev_hook(self):
        try:
            if self.file_list!=[]:
                self.file_index = (self.file_index + len(self.file_list) -1)%len(self.file_list)
                self.image_file_name = self.file_list[self.file_index]
                self.open_file()
        except Exception as error:
            print(error)
        
    def save_to(self, folder):
        try:
            if self.image_file_name == '':
                return
            os.makedirs(folder, exist_ok =True)
            
            v_list = self.algorithm.currentVaules()
            target=self.image_file_name.split('.')
            target[0]+='__'+self.algorithm.getName()+'_'
            for value in v_list:
                target[0]=target[0]+'_'+str(value)
            #print(target[0])
            
            final_img, _ = self.algorithm.adjust(self.original_img,self.img)
            
            if self.off_line.isChecked() and len(final_img)>1 and isinstance(final_img[1], str):
                final_target=os.path.join(folder,str(final_img[1])+'_'+target[0]+'.'+target[1])
            else:
                final_target=os.path.join(folder,target[0]+'.'+target[1])
                


            #print(final_target)
                
            cv2.imwrite(final_target, final_img[0])
            print('Saved!', final_target)
            pass
        except Exception as error:
            print(error)
        
    def send_hook(self):
        try:
            presend_folder=os.path.join(workingdir,PRE_SEND_FOLDER)
            self.save_to(presend_folder)
        except Exception as error:
            print(error)

    def save_hook(self):
        try:
            if self.image_file_name == '':
                return
            save_folder=os.path.join(workingdir,SAVE_FOLDER)
            os.makedirs(save_folder, exist_ok =True)
            cv2.imwrite(os.path.join(workingdir,SAVE_FOLDER,self.image_file_name), self.original_img)
        except Exception as error:
            print(error)
            
    def restore_hook(self):
        try:
            self.algorithm.restore()
            self.setDefault()
            #self.showNew(0,0)
            pass
        except Exception as error:
            print(error)

    def off_line_hook(self):
        try:
            if self.off_line.isChecked():
                print('off line mode')
            else:
                print('on line mode')
            
            pass
        except Exception as error:
            print(error)

    def file_validate(self, file):
        #print(file)
        original_img = cv2.imread(file)
        crop_img = calibration.crop_rotate(original_img)
        newImg, _ = target.adjust(original_img, crop_img)
        return newImg
    
    def folder_validate(self, folder, target):
        print(folder, target)
        files = os.listdir(os.path.join(workingdir,folder))
        match = 0
        fail  = 0
        for each in files:
            if os.path.splitext(each)[1] =='.png':
                result = self.file_validate(os.path.join(workingdir,folder,each))
                if result[1] == target:
                    match+=1
                else:
                    fail+=1
                    print(each)
                    self.file_list.append(os.path.join(workingdir,folder,each))
        print('match: {}, fail: {}, match rate: {}%'.format(match, fail, match*100/(match+fail)))
            
    def group_validate(self, group):
        #print(group)
        for each in group['group']:
            self.folder_validate(each, group['target'])
            
    def validate_hook(self):
        
        invalid  = {
                    'target': str(define.Invalid_image_identifier),
                    'group' : ['invalid']
                    }
        positive = {
                    'target': str(define.Positive_test_result),
                    'group' : ['positive', 'low_positive']
                    }
        negative = {
                    'target': str(define.Negative_test_result),
                    'group' : ['negative', 'fail_negative', 'success_negative', 'tough_negative']
                    }
        unknown  = {
                    'target': str(define.Positive_test_result),
                    'group' : ['weak_positive']
                    }

        checking_list = [invalid, positive, negative, unknown]
        try:
            self.file_list.clear()
            self.validation = True
            self.algorithm = target
            for each in checking_list:
                self.group_validate(each)
            print('validation done')
        except Exception as error:
            print(error)



    def group_hook(self):
        try:
            self.algorithm = self.algs[self.buttonGroup.checkedId()]
            self.setDefault()
            self.showNew(0,0)
        except Exception as error:
            print(error)
    def closeEvent(self,event):
        print("Pop dialog is closing")
        cv2.destroyAllWindows()

def interface():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window=_Improve()
    window.show()
    rtn= app.exec_()
    sys.exit(rtn)
    
    
if __name__ == "__main__":
    interface()
