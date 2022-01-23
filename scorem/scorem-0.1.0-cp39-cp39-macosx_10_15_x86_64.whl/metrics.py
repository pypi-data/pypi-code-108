
import tensorflow as tf

def ssim(image1, image2):
    return tf.image.ssim(image1, image2)
    
    #tf.image.ssim(img1, img2, max_val, filter_size=11, filter_sigma=1.5, k1=0.01, k2=0.03)