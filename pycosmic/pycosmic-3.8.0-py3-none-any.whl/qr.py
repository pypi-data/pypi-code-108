import qrcode 
import cv2 






def encode(text,img_name="image.jpg"):
    cont = qrcode.make(text)
    if img_name is not None:
        cont.save(img_name)
        print(f" Image {img_name} Saved ")
    else:
        print('IMAGE Cannot be None ')


def decode(cont):
    if cont is not None:
        img = cv2.imread(cont)
        decoder = cv2.QRCodeDetector()
        val,a,b = decoder.detectAndDecode(img)

        return val 
    else:
        print('Image Cannot Be None ')



if __name__ == '__main__':
    print(decode('image.jpg'))

        
        
    
    