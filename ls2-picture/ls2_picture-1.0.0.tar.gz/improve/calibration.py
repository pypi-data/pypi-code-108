import cv2
import os
import random
import ntpath

from PIL import Image
import piexif


ROW = 0
COL = 1





IDEAL_BAR_WIDTH = 26
IDEAL_BAR_HEIGHT = 92



MAX_HEIGHT = 1600  ## after 90 degree rotation,
MAX_WIDTH  = 1200

#FIRST_CROP_COL = 80
FIRST_CROP_COL = 215
FIRST_CROP_HEIGHT = IDEAL_BAR_HEIGHT*(min([int(MAX_HEIGHT/IDEAL_BAR_HEIGHT), 8]))
FIRST_CROP_WIDTH  = IDEAL_BAR_WIDTH *(min([int((MAX_WIDTH-FIRST_CROP_COL)/IDEAL_BAR_WIDTH),  30]))
FIRST_CROP_ROW = int((MAX_HEIGHT - FIRST_CROP_HEIGHT)/2) #657



IDEAL_BAR_ROW_OFFSET  = int((FIRST_CROP_HEIGHT - IDEAL_BAR_HEIGHT)/2)
#IDEAL_BAR_COL_OFFSET  = 280
IDEAL_BAR_COL_OFFSET  = 380

CROP_TOP    =[FIRST_CROP_ROW, FIRST_CROP_COL]
CROP_BOTTOM =[FIRST_CROP_ROW+FIRST_CROP_HEIGHT, FIRST_CROP_COL+FIRST_CROP_WIDTH]


##FINAL_HEIGHT = 285
##FINAL_WIDTH  = 740
FINAL_HEIGHT = 320
FINAL_WIDTH  = 780
FINAL_ROW = int((MAX_HEIGHT - FINAL_HEIGHT)/2)
FINAL_COL = FIRST_CROP_COL

FINAL_BAR_ROW = int((FINAL_HEIGHT -IDEAL_BAR_HEIGHT)/2)
FINAL_BAR_COL = IDEAL_BAR_COL_OFFSET

NEGATIVE = 'NEGATIVE'
POSITIVE = 'POSITIVE'
INVALID  = 'INVALID'
##SECOND_BAR_TO_FIRST = 155
##SECOND_BAR_WIDTH = IDEAL_BAR_WIDTH+ 5

##SAMPLE_PIXELS = [[1,1], [100,100], [200,200]]
##
##
##TOP    = [0, IDEAL_BAR_COL_OFFSET - 150]   # row, col
##BOTTOM = [CROP_HEIGHT+EXTEND, IDEAL_BAR_COL_OFFSET + 240] # the range is from TOP  to [BOTTOM[ROW-1], BOTTOM[COL-1]]
##
##TARGET = [20, 10]   # height, width
##TARGET_HEIGHT = 20
##TARGET_WIDTH  = 10
##
##
##HEIGHT = 0
##WIDTH  =1
##
##def isLine(img, begin, end):
##    for c in range(begin[COL], end[COL]):
##        if img[begin[ROW], c] !=0:
##            return False
##    return True
##def isBlock(img, top, bottom):
##    for r in range(top[ROW], bottom[ROW]):
##        if not isLine(img, [r, top[COL]], [r, bottom[COL]]):
##            return False
##    return True
##
##def findTarget(img, top, bottom, target):
##    finalRow = -1
##    finalCol = -1
##    
##    print(top, bottom)
##
##    for c in range(top[COL], bottom[COL] - target[WIDTH]):
##        if finalCol != -1:
##            break;
##        for r in range(top[ROW], bottom[ROW] - target[HEIGHT]):
##            if isBlock(img, [r, c], [r+target[HEIGHT], c+target[WIDTH]]):
##                finalCol = c
##                break;
##    
##    if finalCol == -1:
##        return -1,-1
##
##    print("got col offset ", finalCol)
##    middleR =r-(IDEAL_BAR_HEIGHT-target[HEIGHT])
##    print("middle r ", middleR)
##    for r in range(middleR,  middleR+ (IDEAL_BAR_HEIGHT-target[HEIGHT]) +1):
##        if finalRow != -1:
##            break;
##        for c in range(finalCol, finalCol+IDEAL_BAR_WIDTH-target[WIDTH]):
##            if isBlock(img, [r, c], [r+target[HEIGHT], c+target[WIDTH]]):
##                finalRow = r
##                break;
##
##    return finalRow, finalCol
##
### def findTarget(img, top, bottom, target):
###     finalRow = -1
###     finalCol = -1
###     
###     for c in range(top[COL], bottom[COL] - target[WIDTH]):
###         for r in range(top[ROW], bottom[ROW] - target[HEIGHT]):
###             if isBlock(img, [r, c], [r+target[HEIGHT], c+target[WIDTH]]):
###                 finalCol = c
###                 finalRow = r
###                 break;
###     
###     return finalRow, finalCol
##
##def calibration(img,path):
##    try:
##        
##        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
##        thresh = cv2.threshold(gray, 123, 255, cv2.THRESH_BINARY)[1]
##        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
##        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
##        letter = morph.copy()
##        finalRow, finalCol = findTarget(letter, TOP, BOTTOM, TARGET)
##        cv2.imwrite(os.path.join(path,'gray.jpg'), gray)
##        cv2.imwrite(os.path.join(path,'thresh.jpg'), thresh)
##        cv2.imwrite(os.path.join(path,'letter.jpg'), letter)
##    except Exception as e:
##        print ("calibration exception: ",e)
##        finalRow, finalCol =-1, -1
##    
##    if finalRow == -1 or finalCol == -1:
##        print("calibration failed!")
##        finalRow, finalCol =IDEAL_BAR_ROW_OFFSET+EXTEND, IDEAL_BAR_COL_OFFSET
##    return finalRow, finalCol
##    
##
def cr_size():
    return FIRST_CROP_HEIGHT, FIRST_CROP_WIDTH

def cr(img):
    newImg=cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    cropImg=newImg[FIRST_CROP_ROW:FIRST_CROP_ROW+FIRST_CROP_HEIGHT, FIRST_CROP_COL:FIRST_CROP_COL+FIRST_CROP_WIDTH]
    return cropImg 

def crop_rotate(original_img):
    img = original_img
    if original_img.shape[:2] > cr_size():
        img = cr(original_img)
    return img
 
def final_save(finalImg, imageFile):
    height, width = finalImg.shape[:2]
    print(height, width)
    if height !=FINAL_HEIGHT or width!=FINAL_WIDTH:
        print('wrong picture size')
        return False
    
    cv2.imwrite(imageFile, finalImg)
    
    if os.path.splitext(imageFile)[1] == '.jpg':
        my_exif_ifd = {
                    piexif.ExifIFD.CameraOwnerName: u"Spot II",
                    }
        exif_dict = {"Exif":my_exif_ifd}
        exif_bytes = piexif.dump(exif_dict)
        im = Image.open(imageFile)
        im.save(imageFile, exif=exif_bytes)
        im.close()
    else :
        print('png')
    return True


def cr_modified(img, m_y, m_x):
    newImg=cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    final_row =FINAL_ROW + m_y
    final_col =FINAL_COL + m_x
    cropImg=newImg[final_row:final_row+FINAL_HEIGHT, final_col:final_col+FINAL_WIDTH]
    return cropImg 

#    print("Save image to ",imageFile)
    return True
