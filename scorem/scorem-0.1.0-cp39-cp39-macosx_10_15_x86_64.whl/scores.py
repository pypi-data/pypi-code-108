from os import PathLike
from os import path
import numpy as np
import scorem_core

###############################
#structural correlation index
def SCI(Image1, Image2, sigma=1.0, MaskImage=None):
 shapeImg1=np.shape(Image1)
 shapeImg2=np.shape(Image2)
 if not shapeImg1 == shapeImg2:
     print ('ERROR: images should have same size')
     return -1
 I_fft=np.fft.fft(Image1)
 RI_fft=np.fft.fft(Image2)
 I_abs_fft=np.abs(I_fft)+0.0000001
 RI_abs_fft=np.abs(RI_fft)+0.0000001
 ampAvg=0.5*(I_abs_fft+RI_abs_fft)
 I_out=np.fft.ifft(I_fft*(ampAvg/I_abs_fft)).real.flatten().tolist()
 RI_out=np.fft.ifft(RI_fft*(ampAvg/RI_abs_fft)).real.flatten().tolist()
 if MaskImage==None:
     MaskImage=np.ones( tuple(shapeImg1) )
 MaskImage=MaskImage.flatten().tolist()
 shapeImg1 = shapeImg1 + (1,1,)
 score=scorem_core.MaskedImageComparison(RI_out, I_out, MaskImage, shapeImg1[0], shapeImg1[1], shapeImg1[2],'SCI','None',str(sigma))
 return score

###############################
# Cross Correlation
def CC(Image1, Image2, MaskImage=None):
 #print ('Cross Correlation (CC) \n')
 shapeImg1=np.shape(Image1)
 shapeImg2=np.shape(Image2)
 if not shapeImg1 == shapeImg2:
     print ('ERROR: images should have same size')
     return -1
 if MaskImage==None:
     MaskImage=np.ones( tuple(shapeImg1) )
 Image1=Image1.flatten().tolist()
 Image2=Image2.flatten().tolist()
 MaskImage=MaskImage.flatten().tolist()
 shapeImg1 = shapeImg1 + (1,1,)
 scoreCC=scorem_core.MaskedImageComparison(Image1, Image2, MaskImage, shapeImg1[0], shapeImg1[1], shapeImg1[2], "CC" )
 return scoreCC


def MI(Image1, Image2, MaskImage=None):
 #print ('Mutual Information (MI) \n')
 shapeImg1=np.shape(Image1)
 shapeImg2=np.shape(Image2)
 if not shapeImg1 == shapeImg2:
     print ('ERROR: images should have same size')
     return -1
 if MaskImage==None:
     MaskImage=np.ones( tuple(shapeImg1) )
 Image1=Image1.flatten().tolist()
 Image2=Image2.flatten().tolist()
 MaskImage=MaskImage.flatten().tolist()
 shapeImg1 = shapeImg1 + (1,1,)
 scoreMI=scorem_core.MaskedImageComparison(Image1, Image2, MaskImage, shapeImg1[0], shapeImg1[1], shapeImg1[2], "MI" )
 return scoreMI


def SSIM(Image1, Image2, MaskImage=None):
 #print ('Structural Correlation Index \n')
 shapeImg1=np.shape(Image1)
 shapeImg2=np.shape(Image2)
 if not shapeImg1 == shapeImg2:
     print ('ERROR: images should have same size')
     return -1
 if MaskImage==None:
     MaskImage=np.ones( tuple(shapeImg1) )
 Image1=Image1.flatten().tolist()
 Image2=Image2.flatten().tolist()
 MaskImage=MaskImage.flatten().tolist()
 shapeImg1 = shapeImg1 + (1,1,)
 scoreSSIM=scorem_core.MaskedImageComparison(Image1, Image2, MaskImage, shapeImg1[0], shapeImg1[1], shapeImg1[2], "SSIM" )
 return scoreSSIM

