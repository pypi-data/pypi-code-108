import cv2

def qrIdentify(image):
    decoder = cv2.QRCodeDetector()
    value, points, _ = decoder.detectAndDecode(image)
    print(value)
    try:
        print(points)
        if points.any() == None:
            print('qr')
    except Exception as e:
        return None

    return value
