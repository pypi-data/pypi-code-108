from labelme import Labelme
import cv2

def main():
    labelme1 = Labelme.from_json('assets/sample1.json')
    labelme2 = Labelme.from_json('assets/sample2.json')

    labelme_same = labelme1.intersection(labelme2)
    labelme_diff = labelme1.symmetric_difference(labelme2)

    labelme_same.save_json('tmp/same.json')
    # labelme_diff.save_json('tmp/diff.json')

    image = labelme_diff.load_image(image_root='/home/zhai/Documents/MatrixTime/Huatian/data/')
    image = labelme_diff.draw_shapes(image)
    cv2.imwrite('tmp/diff.jpg', image[...,::-1])


if __name__ == "__main__":
    main()