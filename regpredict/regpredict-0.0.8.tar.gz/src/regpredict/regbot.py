import os
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import joblib
import numpy as np
from pkg_resources import resource_filename
import fire


class Regbot:
  reg_model_path = resource_filename(__name__, 'finalized_model.h5') 
  model_scaler_path = resource_filename(__name__, 'logscaler.gz') 


  def __init__(self,*args):
  	self.model_scaler_path = model_scaler_path

  @classmethod
  def loadmodel(cls):
    loaded_model = joblib.load(open(f'{cls.reg_model_path}', 'rb'))
    return loaded_model


  @classmethod
  def prepareInput(cls,opening,closing,volume):
  	ask_ind = closing*volume/(opening + closing)
  	bid_ind = opening*volume/(opening + closing)
  	testdata = np.array([[ask_ind,bid_ind]])
  	scaler = joblib.load(f'{cls.model_scaler_path}')
  	testdata = scaler.transform(testdata)

  	return testdata


  @classmethod
  def buySignalGenerator(cls,opening,closing,volume):
    scalledInput = cls.prepareInput(opening,closing,volume)
    return cls.loadmodel().predict(scalledInput)[0].round()




def signal(opening,closing,volume):
  try:
    return Regbot.buySignalGenerator(opening,closing,volume)
  except Exception as e:
    print(e)


if __name__ == '__main__':
  fire.Fire(signal)
