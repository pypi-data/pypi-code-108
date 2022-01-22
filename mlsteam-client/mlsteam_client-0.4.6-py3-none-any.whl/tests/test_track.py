import mlsteam
from time import sleep

track = mlsteam.init()
track['config/batch_size']=32
track['accuracy'].log(0.5)
track['accuracy'].log(0.6)
track['accuracy'].log(0.7)
#track.stop()
