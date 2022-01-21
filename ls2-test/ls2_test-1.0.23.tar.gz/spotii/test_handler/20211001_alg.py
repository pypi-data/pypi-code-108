import os
from abc import ABC, abstractmethod
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import calibration
import define



class Algorithm(ABC):
    def __init__(self,name,v_list):
        self.name =name
        self.v=v_list.copy()
        self.default=v_list.copy()
        self.originalImage=[]
        self.simple = False
        self.chart  = False
    def defaultVaules(self):
        return self.default
    def currentVaules(self):
        return self.v
    def getName(self):
        return self.name
    def restore(self):
        self.v = self.default.copy()
    def modify(self, index, value):
        if index in range(len(self.v)):
            self.v[index] = self.default[index] + value
            return self.v[index]
        return 0
        
    def adjust(self,original,img,index=None, value=None, simple = False, chart = False):
        self.simple = simple
        self.chart  = chart
        plt_close()
        self.originalImage = original
        if index == None or value == None:
            new_value = None
        else:
            new_value = self.modify(index,value)
        cal_result=self.calculation(img)
        #horizontalStack = np.concatenate((img, cal_result), axis=1)
        return cal_result, new_value
    @abstractmethod
    def calculation(self, image):
        pass


def plt_show(b=None, g=None, r=None, av=None):
    for y in [b,g,r,av]:
        if y !=None:
            break;
    if y == None:
        return;
        
    x=[]
    for i in range(len(y)):
        x.append(i)

    if b!=None:
        #print('show b')
        plt.plot(x, b,  color='blue', label="mean")
    if g!=None:
        #print('show g')
        plt.plot(x, g,  color='green', label="green")
    if r!=None:
        #print('show r')
        plt.plot(x, r,  color='red', label="Filtered mean")
    if av!=None:
        #print('show av')
        plt.plot(x, av,  color='black', label="standard deviation")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.ylim(0, 255)
    plt.legend()
    plt.show()

def plt_close():
    plt.close()
    
class Target(Algorithm):
    def threshold(self, img, MAX_STDD, MIN_STDD):
        low = 0
        high = 255
        while True:
            mid = int((low + high)/2)
            #print(low, high, mid)
            thresh = cv2.threshold(img, mid, 255, cv2.THRESH_BINARY)[1]
            mean, std = cv2.meanStdDev(thresh)
            #print(mean,std)
            std = int(std)
            print('std', std)
            if std in range(MIN_STDD, MAX_STDD):
                break;
            if std < MIN_STDD:
                low = mid
            else:
                high = mid
            if low == high:
                break;
        return thresh, std

    def channel_deal(self, ch, ref):
        rev=cv2.bitwise_not(ch)
        _,trunck = cv2.threshold(rev, ref, 255, cv2.THRESH_TRUNC)
        back = cv2.bitwise_not(trunck)

##        cv2.imshow('original', ch)
##        cv2.imshow('rev', rev)
##        cv2.imshow('trunck', trunck)
##        cv2.imshow('back', back)
##        cv2.waitKey(0)
        return back

    def dark_filter(self, img, ref_bgr):
        
        b, g, r = cv2.split(img)
        b1 = self.channel_deal(b, ref_bgr[0])
        g1 = self.channel_deal(g, ref_bgr[1])
        r1 = self.channel_deal(r, ref_bgr[2])
        result = cv2.merge([b1,g1,r1])
        return result

    def h_f(self, img, area, target_width):    #area [x:,y:, width:, height:], return area with min mean
        total_range = area['width']
        start = area['x']

        mn_list = []
        #print(total_range, start)
        while total_range > 0:
            if target_width < total_range:
                step = target_width
            else :
                step = total_range
            mean, stdev =cv2.meanStdDev(img[area['y']:area['y']+area['height'], start:start+step])

            mn  = int(mean[0][0])
            mn_list.append(mn)
            if(start!=area['x']):
                mn_list[-2] += mn_list[-1]
            #print(start, mn )
            total_range -= step
            start+=step

        mn_list.pop()
        #print('h_f  mn_list', mn_list)
        min_index = mn_list.index(min(mn_list))
        #print('min  mn index', min_index, mn_list[min_index])

        result = {
            'x' : min_index * target_width,
            'y' : area['y'],
            'width' : 2*target_width,
            'height': area['height']
            }
        #print(result)
        total = target_width
        while total >0:
            cut_off = int(total/2)
            if cut_off ==0 :
                cut_off =1
            mean, stdev =cv2.meanStdDev(img[result['y']:result['y']+result['height'], result['x']:result['x']+cut_off])
            front_mn  = int(mean[0][0])
            mean, stdev =cv2.meanStdDev(img[result['y']:result['y']+result['height'], result['x']+result['width']-cut_off:result['x']+result['width']])
            tail_mn  = int(mean[0][0])
            if front_mn > tail_mn:
                result['x'] += cut_off
            result['width'] -= cut_off
            total -= cut_off
        return result

    def v_f(self, img, area, target_height):
        total_range = area['height']
        start = area['y']
        mn_list = []
        #print('v_f lef_range target_height', total_range, target_height)
        while total_range > 0:
            if target_height < total_range:
                step = target_height
            else :
                step = total_range
            mean, stdev =cv2.meanStdDev(img[start:start+step, area['x']:area['x']+area['width']])
            mn  = int(mean[0][0])
            mn_list.append(mn)
            if(start!=area['y']):
                mn_list[-2] += mn_list[-1]
            total_range -= step
            start+=step
        mn_list.pop()
        #print('v_f mn_list', mn_list)
        min_index = mn_list.index(min(mn_list))
        #print('min index',min_index, mn_list[min_index])
        result = {
            'x' : area['x'],
            'y' : min_index * target_height,
            'width' : area['width'],
            'height': 2*target_height
            }

        
        total = target_height
        while total >0:
            cut_off = int(total/2)
            if cut_off ==0 :
                cut_off =1
            #print(result['y'], result['y']+cut_off, result['x'], result['x']+result['width'])
            mean, stdev =cv2.meanStdDev(img[result['y'] : result['y']+cut_off, result['x']:result['x']+result['width']])
            front_mn = int(mean[0][0])
            #print(result['y']+result['height']-cut_off, result['y']+result['height'], result['x'], result['x']+result['width'])
            mean, stdev =cv2.meanStdDev(img[result['y']+result['height']-cut_off : result['y']+result['height'], result['x']:result['x']+result['width']])
            tail_mn = int(mean[0][0])
            if front_mn > tail_mn:
                result['y'] += cut_off
            result['height'] -= cut_off
            total -= cut_off
        return result
        
    def areaFilter(self, img, area, target_size):  #target_size [height, width], return area list
        #print('areaFilter')
        h_f_result = self.h_f(img, area, target_size[1])
        #print (h_f_result)
        v_f_result = self.v_f(img, h_f_result, target_size[0])
        #print (v_f_result)
        return v_f_result

    def channel_increase(self, c, value):
        if value >0:
            #print('increase', value)
            lim = 255 - value
            c[c > lim] = 255          
            c[c <= lim] += value
        else:
            #print('decrease', value)
            lim = abs(value)
            c[c < lim] = 0
            c[c >= lim] -= lim            
        return c
        
    def bright(self,img, value):
        b, g, r = cv2.split(img)
        b = self.channel_increase(b, value)
        g = self.channel_increase(g, value)
        r = self.channel_increase(r, value)
        final_img = cv2.merge((b, g, r))
        return final_img

    def balance(self,img, average):
        mean, stdev =cv2.meanStdDev(img)
        mn_list = [int(mean[0][0]), int(mean[1][0]), int(mean[2][0])]
        #average = int(sum(mn_list)/len(mn_list))
        #average = 230
        b, g, r = cv2.split(img)
        b = self.channel_increase(b, average - mn_list[0]+8)
        g = self.channel_increase(g, average - mn_list[1]-5)
        r = self.channel_increase(r, average - mn_list[2]-1)
        final_img = cv2.merge((b, g, r))
        return final_img

    def gauss(self, image):
        kernel = np.array([[0, -1, 0],[-1, 5, -1],[0, -1, 0]], np.float32)
        result = cv2.filter2D(image, -1, kernel=kernel)
        return result

    def color_zhi_fang(self, image):

        b, g, r = cv2.split(image)
        
        b1 = cv2.equalizeHist(b)
        #b1 = np.hstack((b,b1))
        
        g1 = cv2.equalizeHist(g)
        #g1 = np.hstack((g,g1))

        r1 = cv2.equalizeHist(r)
        #r1 = np.hstack((r,r1))
         
        result = cv2.merge([b1,g1,r1])
        return result


    def clahe(self, image):

        b, g, r = cv2.split(image)
#        clahe = cv2.createCLAHE(clipLimit=29.0, tileGridSize=(1,13))

#        clahe = cv2.createCLAHE(clipLimit=29.0, tileGridSize=(11,21))

        clahe = cv2.createCLAHE(clipLimit=45.0, tileGridSize=(9,40))
        

#        clahe = cv2.createCLAHE(clipLimit=29.0, tileGridSize=(1,6))

        #clahe = cv2.createCLAHE(clipLimit=0.0, tileGridSize=(13,13))
        #clahe = cv2.createCLAHE()
        
        b1 = clahe.apply(b)
        
        g1 = clahe.apply(g)

        r1 = clahe.apply(r)
         
        result = cv2.merge([b1,g1,r1])
        return result
#horizontalStack = np.concatenate((self.img, self.newImg), axis=1)

    def edsr(self,img):
#        result = cv2.resize(img,dsize=None,fx=4,fy=4)
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        path = os.path.join(currentdir,"EDSR_x4.pb")
        sr.readModel(path)
        sr.setModel("edsr", 4) # set the model by passing the value and the upsampling ratio
        result = sr.upsample(img) # upscale the input image
        return result

    def filt(self, original_list, adjust):
        average = sum(original_list)/len(original_list)
        average += adjust
        if average > 255:
            average =255
        elif average < 0:
            average = 0
        minium  = min(original_list)
        maxim   = max(original_list)
        rtn_list = []
        for each in original_list:
            if each < average:
                rtn_list.append(minium)
            else:
                rtn_list.append(maxim)
        return rtn_list
            

    def filt_width(self, original_list, number,std_list, max_std, min_diff):
        sort_list=original_list.copy()
        sort_list.sort()

        av_std=sum(std_list)/len(std_list)
        
        average = sort_list[number-1]
        #average = sum(original_list)/len(original_list)

        
        maxim=sort_list[-1]
        
        rtn_list = []
        for each in original_list:
            if each>average : ## and (each - average) >10:
                rtn_list.append(maxim)
            elif (std_list[original_list.index(each)]-av_std)>max_std and std_list[original_list.index(each)]>30:
                pass
            elif (average - each) < min_diff:
                pass
            else:
                rtn_list.append(average)
        #print('rtn_list', rtn_list)
        i =0
        for each in rtn_list:
            if each == maxim:
                break;
            rtn_list[i] =maxim
            i+=1
        #print('fix head', rtn_list)
        i=len(rtn_list)
        for each in reversed(rtn_list):
            i -=1
            if each == maxim:
                break;            
            rtn_list[i]=maxim
        #print('fix tail', rtn_list)
        return rtn_list

    def filt_width_no_std(self, original_list, number):
        sort_list=original_list.copy()
        sort_list.sort()

        
        average = sort_list[number-1]
        maxim=sort_list[-1]
        rtn_list = []
        for each in original_list:
            if each>average:
                rtn_list.append(maxim)
            else:
                rtn_list.append(average)
        return rtn_list

        
        
    def av_mean_draw(self, image, barWidth, ch):
        height,width =image.shape[:2]
        
        mn_list  = []
        std_list = []
        x=0
        while width > 0:
            bar = image[0:height, x:x+barWidth]
            mn, std = self.mean_std(bar, ch)
            mn_list.append(mn)
            std_list.append(std)
            x+=barWidth
            width -=barWidth
        return mn_list, std_list

    

    def block_mean_std(self, image, i):
        mean, stdev =cv2.meanStdDev(image)
        mn_list=[int(mean[0]), int(mean[1]), int(mean[2])]
        st_list=[int(stdev[0]), int(stdev[1]), int(stdev[2])]
        if i < len(mn_list):
            rtn = mn_list[i] # g channel, lower mean more red color
            std = st_list[i]
        else:
            rtn = int(sum(mn_list)/len(mn_list))
            std = int(sum(st_list)/len(st_list))
        
        #print(rtn , mn_list)
        return rtn, std


    def mean_std(self, image, i):
        num =1
        height, width = image.shape[:2]
        step= int(height/num)
        start =0
        mn_list=[]
        std_list =[]
        for i in range(num):
            block = image[start:start+step, 0:width]
            mn, std = self.block_mean_std(block,i)
            mn_list.append(mn)
            std_list.append(std)
            start+=step
        
        max_mn = max(mn_list)
        m_index = mn_list.index(max_mn)
        max_mn_std = std_list[m_index]
        return max_mn, max_mn_std



    def av_mean(self, image, i):
        
        
        mean, stdev =cv2.meanStdDev(image)
        mn_list=[int(mean[0]), int(mean[1]), int(mean[2])]
        if i < len(mn_list):
            rtn = mn_list[i] # g channel, lower mean more red color
        else:
            rtn = sum(mn_list)/len(mn_list)
        
        #print(rtn , mn_list)
        return rtn

    def barIdt(self, image, offset, width):
        reduce =10
        height, _ = image.shape[:2]        
        mid       = image[0: height,
                            offset: offset+width]                            
        left      = image[0: height,
                            offset-(width-reduce): offset]                            
        right     = image[0: height,
                            offset+width: offset+width+(width - reduce)]

        down_mn    =[self.av_mean(left,1), self.av_mean(mid,1), self.av_mean(right,1)]
        down_block =[left,mid,right]
        print(down_mn)

        rtn =False
        if down_mn[1] == min(down_mn):
            if down_mn[1]>90:
                rtn =True
        return rtn , [left,mid,right]

    def lightBarConfirm(self, mn_list, deep, width):
        value = min(mn_list)
        if value == max(mn_list):
            #print('Negative')
            return define.Negative_test_result
        length = []
        count = 0
        for each in mn_list:
            if each == value:
                count+=1
            else:
                if count!=0:
                    length.append(count)
                count=0
        if count!=0:
            length.append(count)
        
        max_width = max(length)
        #print(max_width, length)
#        if value > deep and max_width > width:
        if max_width > width:
            #print('Positive')
            return define.Positive_test_result
        #print('Negative')
        return define.Negative_test_result
##    
##MIN_STDD = 20
##MAX_STDD = 25

        
    def calculation(self, image):
        #print('original',image.shape[:2])
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh, std = self.threshold(gray, 25, 20)
        #print('target std',std)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,8))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        height,width = morph.shape[:2]

        if(height == calibration.FINAL_HEIGHT and width == calibration.FINAL_WIDTH): ## For those pictures from server or dash board
            blc = image
        else:
            area = {
                'x' : 0,
                'y' : 0,
                'width' : width,
                'height': height
                }
            #print('area', area)
            target_area=self.areaFilter(morph, area, [calibration.IDEAL_BAR_HEIGHT, calibration.IDEAL_BAR_WIDTH])
            #print('idea bar col, row', calibration.IDEAL_BAR_COL_OFFSET, calibration.IDEAL_BAR_ROW_OFFSET)
            #print('target_area', target_area)
     
            target_crop =morph[target_area['y']:target_area['y']+target_area['height'],
                               target_area['x']:target_area['x']+target_area['width']]

        
            mean, stdev =cv2.meanStdDev(target_crop)

            mn = int(mean[0][0])
        
            blank = False
            if mn >  115: ## Blank cassette
                m_x =0
                m_y =0
                blank = True
                #print('blank')
            else:
                m_x = target_area['x'] - calibration.IDEAL_BAR_COL_OFFSET
                m_y = target_area['y'] - calibration.IDEAL_BAR_ROW_OFFSET
                cal = calibration.cr_modified(self.originalImage, m_y, m_x)
                cal_h, cal_w = cal.shape[:2]
                #print(cal_h,cal_w)
                if cal_h != calibration.FINAL_HEIGHT or cal_w != calibration.FINAL_WIDTH: #out of range, wrong bar position detection
                    #print('wrong bar position')
                    blank = True

            if blank:
                final = calibration.cr_modified(self.originalImage, 0, 0)
                #print('Invalid')
                return [final, str(define.Invalid_image_identifier)]

            cal = calibration.cr_modified(self.originalImage, m_y, m_x)
            blc = self.balance(cal,198)
            
        #if sys.platform != 'win32':   ## balancing only 
        if self.simple == True:        ## balancing only
            return[blc, str(define.Unknown)]
        clh = self.clahe(blc)
        secondBarToFirst = 160
        secondBarWidth = calibration.IDEAL_BAR_WIDTH+4

        reduce = 10
        weak_height = calibration.IDEAL_BAR_HEIGHT -reduce*2
        weak_row_start = calibration.FINAL_BAR_ROW + reduce        

        block_offset =142
        block_width  = calibration.IDEAL_BAR_WIDTH*3 #calibration.IDEAL_BAR_WIDTH*2+ int(calibration.IDEAL_BAR_WIDTH/2)
        sample_width = 1#int(calibration.IDEAL_BAR_WIDTH/16)
        block = clh[ weak_row_start: weak_row_start+weak_height,
                              calibration.FINAL_BAR_COL+block_offset : calibration.FINAL_BAR_COL+block_offset + block_width]

        nice_block = blc[ weak_row_start: weak_row_start+weak_height,
                              calibration.FINAL_BAR_COL+block_offset : calibration.FINAL_BAR_COL+block_offset + block_width]

        
        b = 0
        g = 1
        r = 2
        av =3

        mn_list, std_list = self. av_mean_draw(block, sample_width, g)


##        std_filter = 6
##        mn_filter  = 100
##        width_filter = 13      # 0.0, 13,13
##        number_of_low_mn = 26#30 #calibration.IDEAL_BAR_WIDTH

        std_filter = 6
        mn_filter  = 100
        width_filter = 10      # 0.0, 13,13
        number_of_low_mn = 36#30 #calibration.IDEAL_BAR_WIDTH
        min_diff   = 5
        

        filt_width_list = self.filt_width(mn_list, number_of_low_mn, std_list, std_filter, min_diff)
#        if sys.platform == 'win32':
        if self.chart == True:
            plt_show(av=std_list, b=mn_list)
            plt_show(r=filt_width_list)
        


        rtn = self.lightBarConfirm(filt_width_list, mn_filter, width_filter)
        
        final = blc
##        firstBar = final[calibration.FINAL_BAR_ROW: calibration.FINAL_BAR_ROW+calibration.IDEAL_BAR_HEIGHT,
##                       calibration.FINAL_BAR_COL: calibration.FINAL_BAR_COL+calibration.IDEAL_BAR_WIDTH]
##        if rtn:
##            firstBar = self.bright(firstBar,90)
##            secondBar = firstBar
##            final[calibration.FINAL_BAR_ROW: calibration.FINAL_BAR_ROW+calibration.IDEAL_BAR_HEIGHT,
##                           calibration.FINAL_BAR_COL+secondBarToFirst: calibration.FINAL_BAR_COL+ secondBarToFirst+calibration.IDEAL_BAR_WIDTH] = firstBar
##        


        return [final, str(rtn) ,clh, block]

        nice_gray = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
        nice_thresh, std = self.threshold(nice_gray, 100, 80)
        #print('target std',std)
        nice_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,8))
        nice_morph = cv2.morphologyEx(nice_thresh, cv2.MORPH_OPEN, nice_kernel)
        return [final, str(rtn) ,clh, block, nice_morph]
        
        
            
        r =80
        h   =160 
        top = final[r:r+h,0:width]
        bottom = clh[r:r+h,0:width]
        combine = np.concatenate((top, bottom), axis=0)
        return [combine, str(rtn) ,clh, block]
        



        weak = clh[ weak_row_start: weak_row_start+weak_height,
                              calibration.FINAL_BAR_COL : calibration.FINAL_BAR_COL+secondBarToFirst + secondBarWidth*2]
        rtn, bar_list = self. barIdt(weak, secondBarToFirst, secondBarWidth)

        
        
        final = blc
        firstBar = final[calibration.FINAL_BAR_ROW: calibration.FINAL_BAR_ROW+calibration.IDEAL_BAR_HEIGHT,
                       calibration.FINAL_BAR_COL: calibration.FINAL_BAR_COL+calibration.IDEAL_BAR_WIDTH]
        if rtn:
            firstBar = self.bright(firstBar,70)
            secondBar = firstBar
            final[calibration.FINAL_BAR_ROW: calibration.FINAL_BAR_ROW+calibration.IDEAL_BAR_HEIGHT,
                           calibration.FINAL_BAR_COL+secondBarToFirst: calibration.FINAL_BAR_COL+ secondBarToFirst+calibration.IDEAL_BAR_WIDTH] = firstBar
#        return [morph, target_crop, final]
        #return [blc, clh, weak, second_left, second ,second_right]
        return [final, block]
#        return [final, confirm]+confirm_bar_list

    
class Nothing(Algorithm):
    def calculation(self, image):
        return [image]

    
class BackRgb(Algorithm):
    def calculation(self, image):
        gray_three = cv2.merge([image,image,image])
        #backtorgb = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)
        return [gray_three]
#THRESH_TRUNC
#THRESH_BINARY
#THRESH_BINARY_INV
#THRESH_TOZERO
#THRESH_TOZERO_INV
class Gray(Algorithm):
    def calculation(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

##        b, g, r = cv2.split(image)
##        gray = g
        thresh = cv2.threshold(gray, self.v[0], self.v[1], cv2.THRESH_BINARY)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.v[2],self.v[3]))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        return [morph]

class Linar_gray(Algorithm):
    def calculation(self, img):
        a = self.v[0] #2
        O = float(a) * img
        O[O>255] = 255 #大于255要截断为255
            
        #数据类型的转换
        O = np.round(O)
        O = O.astype(np.uint8)
        return [O]

    
class Gauss(Algorithm):
    def calculation(self, image):
        gaussianBlurKernel = np.array((self.v[:3], self.v[3:6], self.v[6:9]), np.float32)/self.v[9]
        gaussianBlur = cv2.filter2D(src=image, kernel=gaussianBlurKernel, ddepth=-1)
        return [gaussianBlur]

    
class Custom_blur(Algorithm):
    def calculation(self, image):
        #kernel = np.ones([5, 5], np.float32)/25
        kernel = np.array([[0, -1, 0],[-1, 5, -1],[0, -1, 0]], np.float32)
        dst = cv2.filter2D(image, -1, kernel=kernel)
        return [dst]


class Contrast(Algorithm):
    def modify(self, index, value):
        if index in range(len(self.v)):
            if index == 0:
                multi = 0.1
            elif index == 1:
                multi = 5
            self.v[index] = self.default[index] + multi*value
            return self.v[index]
        return 0  
    def calculation(self, image):
        adjusted = cv2.convertScaleAbs(image, alpha=self.v[0], beta=self.v[1])
        return [adjusted]

class MeanBlur(Algorithm):
    def calculation(self, image):
        meanBlurKernel = np.ones((self.v[0], self.v[1]), np.float32)/self.v[2]
        meanBlur = cv2.filter2D(src=image, kernel=meanBlurKernel, ddepth=-1)
        return [meanBlur]

class Color_zhi_fang(Algorithm):
    def calculation(self, image):

        b, g, r = cv2.split(image)
        
        b1 = cv2.equalizeHist(b)
        g1 = cv2.equalizeHist(g)
        r1 = cv2.equalizeHist(r)
         
        result = cv2.merge([b1,g1,r1])
        return [result]

class Split(Algorithm):
    def calculation(self, image):

        b, g, r = cv2.split(image)
        b1 = cv2.equalizeHist(b)
        g1 = cv2.equalizeHist(g)
        
        new=cv2.merge([g1,b,r])
        return [b,g,r,new]

class HisEqulColor(Algorithm):
    def calculation(self,img):
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)  
        channels = cv2.split(ycrcb)  
        cv2.equalizeHist(channels[0], channels[0]) #equalizeHist(in,out)  
        cv2.merge(channels, ycrcb)  
        img_eq=cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR)  
        return [img_eq]


class Brightness(Algorithm):
    def calculation(self,img):

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        lim = 255 - self.v[0]
##        v[v > lim] = 255
##        v[v <= lim] += self.v[0]
##        s[s > lim] = 255
##        s[s <= lim] += self.v[0]
        h[h > lim] = 255
        h[h <= lim] += self.v[0]

        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return [img]

class Histogram_gray(Algorithm):
    def calculation(self, image):
        # create a CLAHE object (Arguments are optional).
        #clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        clahe = cv2.createCLAHE(clipLimit=self.v[0], tileGridSize=(self.v[1],self.v[2]))
        cl1 = clahe.apply(image)
        return [cl1]

class Clahe(Algorithm):
##    def modify(self, index, value):
##        if index in range(len(self.v)):
##            if index == 0:
##                multi = 0.1
##            else:
##                multi = 1
##            self.v[index] = self.default[index] + multi*value
##            return self.v[index]
##        return 0   

    def calculation(self, image):
        b, g, r = cv2.split(image)
        clahe = cv2.createCLAHE(clipLimit=self.v[0], tileGridSize=(self.v[1],self.v[2]))
        
        b1 = clahe.apply(b)
        g1 = clahe.apply(g)
        r1 = clahe.apply(r)
         
        result = cv2.merge([b1,g1,r1])
        return [result]

class HE_ycrcb(Algorithm):
    def calculation(self, rgb_img):

        # convert from RGB color-space to YCrCb
        ycrcb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2YCrCb)

        # equalize the histogram of the Y channel
        ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])

        # convert back to RGB color-space from YCrCb
        equalized_img = cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2BGR)
        return [equalized_img]

class White_balance(Algorithm):
    def calculation(self, img):
        rows = img.shape[0]
        cols = img.shape[1]
        final = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(final[:,:,1])
        avg_b = np.average(final[:,:,2])
        for x in range(final.shape[0]):
            for y in range(final.shape[1]):
                l,a,b =final[x,y,:]
                # fix for CV correction
##                l *=100 / 256.0
##                final[x,y,1] = a - ((avg_a -128) * (l / 100.0) * 1.0)
##                final[x,y,2] = b - ((avg_b -128) * (l / 100.0) * 1.0)
                #l *=(1.0 / 256.0
                l = l/256.0
                final[x,y,1] = a - ((avg_a -128) * l)
                final[x,y,2] = b - ((avg_b -128) * l)
        final = cv2.cvtColor(final, cv2.COLOR_LAB2BGR)
        return [final]

class Wb_xphoto(Algorithm):
    def modify(self, index, value):
        if index in range(len(self.v)):
            if index == 0:
                multi = 0.01
            else:
                multi = 1
            self.v[index] = self.default[index] + multi*value
            return self.v[index]
        return 0   
    def calculation(self, image):
        wb = cv2.xphoto.createGrayworldWB()
        wb.setSaturationThreshold(self.v[0])#0.99
        wb.balanceWhite(image, image)
        return image


class Normalize(Algorithm):
    def modify(self, index, value):
        if index in range(len(self.v)):
            if index == 0:
                multi = 10
            elif index == 1:
                multi = 1
            self.v[index] = self.default[index] + multi*value
            return self.v[index]
        return 0   
    def calculation(self, image):
        result = cv2.normalize(image,dst=None,alpha=self.v[0],beta=self.v[1],norm_type=cv2.NORM_MINMAX)
        return [result]

  
class Stretch_min_max(Algorithm):
    def calculation(self, image):
##        xp = [0, 64, 128, 192, 255]
##        fp = [0, 16, 128, 240, 255]
        xp = [0, self.v[0], self.v[1], self.v[2], 255]
        fp = [0, self.v[3], self.v[4], self.v[5], 255]
        x = np.arange(256)
        table = np.interp(x, xp, fp).astype('uint8')
        result = cv2.LUT(image, table)
        return [result]


class Simplest_cb(Algorithm):
    def calculation(self,img):
        percent=self.v[0]
        out_channels = []
        cumstops = (
            img.shape[0] * img.shape[1] * percent / 200.0,
            img.shape[0] * img.shape[1] * (1 - percent / 200.0)
        )
        for channel in cv2.split(img):
            cumhist = np.cumsum(cv2.calcHist([channel], [0], None, [256], (0,256)))
            low_cut, high_cut = np.searchsorted(cumhist, cumstops)
            lut = np.concatenate((
                np.zeros(low_cut),
                np.around(np.linspace(0, 255, high_cut - low_cut + 1)),
                255 * np.ones(255 - high_cut)
            ))
            out_channels.append(cv2.LUT(channel, lut.astype('uint8')))
        return [cv2.merge(out_channels)]

class Gamma(Algorithm):
    def modify(self, index, value):
        multi = 0.1
        self.v[index] = self.default[index] + multi*value
        return self.v[index]
    
    def calculation(self, image):
        fI = image/255.0
        gamma = self.v[0] #0.4
        return [np.power(fI, gamma)]

class AddWeight(Algorithm):
    def modify(self, index, value):
        if index == 0:
            multi = 0.1
        elif index == 1:
            multi = 1
        
        self.v[index] = self.default[index] + multi*value
        return self.v[index]
    def calculation(self, img1):
        c=self.v[0]  # (1.3, 3 )亮度就是每个像素所有通道都加上b
        b=self.v[1]
        rows, cols, channels = img1.shape
        # 新建全零(黑色)图片数组:np.zeros(img1.shape, dtype=uint8)
        blank = np.zeros([rows, cols, channels], img1.dtype)
        dst = cv2.addWeighted(img1, c, blank, 1-c, b)
        return [dst]

class Bilateral(Algorithm):
    def calculation(self,img):
        sigmaColor = self.v[0] * 10
        sigmaSpace = sigmaColor*2
        imgb = cv2.bilateralFilter(img, 100, sigmaColor, sigmaSpace)
        return [imgb]

class EDSR(Algorithm):
    def calculation(self,img):
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        path = "EDSR_x4.pb"
        sr.readModel(path)
        sr.setModel("edsr", 4) # set the model by passing the value and the upsampling ratio
        result = sr.upsample(img) # upscale the input image
        return [result]


nothing = Nothing('Original',[]) 
gauss = Gauss('gauss', [-1, 1, -1, 2, 6, 2, 1, 1, -6, 9])
contrast = Contrast('conrast',[1,0])
meanBlur = MeanBlur('meanBlur',[3,3,9])
his_equl_c_1 = Color_zhi_fang('his_equl_c_1',[])
normalize = Normalize('normalize',[350,10])
#stretch    = Stretch_min_max([64, 128, 192, 16, 128, 240])
stretch    = Stretch_min_max('stretch',[0, 158, 255, 0, 47, 255])
simplest_cb = Simplest_cb('simplest_cb',[1])
his_equl_c_2 = HisEqulColor('his_equl_c_2',[])
#white_balance = White_balance('white balance',[1, 1.1, 1, 1.1])
white_balance = White_balance('white balance',[])
custom_blur =Custom_blur('custom blur',[])
gray = Gray('gray',[123,255,7,7])
linar_gray = Linar_gray('linar_gray',[2])
backRgb = BackRgb('backRgb',[])
split = Split('split',[])
gamma = Gamma('gamma',[0.4])
addWeight = AddWeight('addWeight', [1.3, 3])
wb_xphoto = Wb_xphoto('wb_xphoto',[0.99])
target = Target('target',[])
histogram_gray = Histogram_gray('histogram_gray', [2.0, 8, 8])
brightness = Brightness('brightness',[20])

clahe = Clahe('clahe',[2.0, 8, 8])
he_ycrcb = HE_ycrcb('he_ycrcb',[])

bilateral = Bilateral('bilateral',[1])

edsr = EDSR('edsr',[])
