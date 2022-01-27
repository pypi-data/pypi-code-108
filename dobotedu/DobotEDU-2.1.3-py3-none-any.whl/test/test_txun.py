from playsound import playsound
import os
from DobotEDU import DobotEDU
import base64
from scipy.io.wavfile import write

def to_base64(file_name):  #转化为Base64格式
    with open(file_name,'rb') as f:
        base64_data = base64.b64encode(f.read())
        return base64_data

def asr(file_name):  #语音识别
    audio_data = to_base64(file_name)
    result = speech.asr(audio_data)
    print(result)
    return result

def tts(text):  #语音合成
    audio = speech.synthesis(text,"1")
    with open("audio.mp3",'wb') as f:
        f.write(audio)
    playsound("audio.mp3")
    os.remove("audio.mp3")

def record(file_name,count_down):  #录音
    print("录音开始...")
    myrecording = util.record(count_down)
    print("录音结束...")
    write(file_name, 16000, myrecording)  # 保存为一个WAV文件)
    
# 定义机器人对话函数
def robot_conver():
    session_id = ""
    filename = "audio.wav"
    while True:
        record(filename,4)
        query = asr(filename)
        ret = robot.conversation(query, session_id)
        #print(ret)
        val = 'result' in ret.keys()
        result = ''
        if val == True:
            result = ret['result']['response_list'][0]['action_list'][0]['say']
            print(result)
            tts(result)
            session_id = ret['result']['session_id']
        else:
            print('None')

robot_conver()