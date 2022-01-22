from multiprocessing import Process 
import time 
import os 
def run_kwin():
    os.system('kwin --replace')
t = Process(target = run_kwin)
t.start()
time.sleep(1)
t.terminate()
os.system('killall kwin')