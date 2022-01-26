import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.dates as mdates
import json
from matplotlib.font_manager import FontProperties
from pathlib import Path 
import os 
import click
try:
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtCore import Qt,QTimer
    from PyQt5.QtGui import QPixmap
except:
    pass

sns.set_theme(style="dark")

def Gantt(csv,color = ('tomato','wheat'),width=9,gap=4,font_file=None,output=None,figsize=(10,6)):
    if Path(csv).suffix == '.csv':
        df = pd.read_csv(csv)
    else:
        df = pd.read_excel(csv)
    df = df.iloc[::-1]
    keys = list(df.keys())
    mission_name = df[keys[0]]
    date0 = df[keys[1]].iloc[0]
    if date0.find('日') != -1:
        df[keys[1]] = df[keys[1]].str.replace('月','-')
        df[keys[1]] = df[keys[1]].str.replace('日','')
        df[keys[1]] = df[keys[1]].str.replace('年','-')
    if date0.find('/') != -1:
        df[keys[1]] = df[keys[1]].str.replace('/','-')
    date0 = df[keys[1]].iloc[0]
    today = datetime.today()
    if len(date0)>5:
        is_year=True 
    else:
        is_year=False
        xs = [datetime.strptime(d+'-'+str(today.year),'%m-%d-%Y') for d in df[keys[1]]]

        

    if not font_file:
        p = Path(os.environ['HOME']) /'.cache'/'matplotlib'
        json_path = list(p.glob('*.json'))[0]
        json_data = json.load(open(json_path))
        for i in json_data['ttflist']:
            if i['name'] == 'SimHei':
                font_file = i['fname']
                break
    font = FontProperties(fname=font_file)
    fig, ax = plt.subplots(figsize=figsize)
    gw = gap + width
    d0 = timedelta(0)
    for ii, (i,delta) in enumerate(zip(xs,df[keys[2]])):
        dd = timedelta(delta)
        du = max(d0,min(today-i,dd))
        if du>d0:
            ax.broken_barh([(i,dd),[i,du]], (10+ii*gw, width), color=color)
        else:
            ax.broken_barh([(i,dd)], (10+ii*gw, width), color=color[0])
    if is_year:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    # ax.set_xlabel(xlabel)
    ax.xaxis.tick_top()
    # ax.minorticks_off()
    ax.tick_params(direction='in',length=0.1)
    ax.set_yticks([10+width/2+i*gw for i in range(len(mission_name))])
    ax.set_yticklabels(mission_name,fontproperties=font)
    ax.grid(True)
    if output:
        plt.savefig(output,bbox_inches='tight')

def display_gantt_on_desktop(gp_name,opacity=0.85,position=None,title_bar=False,delete_temp=False,gantt_params=None):
    def update_img(*d):
        Gantt(*gantt_params)
        t = QPixmap(gp_name)
        w.setPixmap(t)
        if delete_temp:
            os.remove(gp_name)
        return t
    app = QApplication(sys.argv)
    w = QLabel()
    desktop = app.desktop()
    if not title_bar:
        w.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint | Qt.WindowDoesNotAcceptFocus)
    t = update_img()
    w.setWindowOpacity(opacity)
    if len(position.split(','))==1:
        if position.find('top') != -1:
            hp = 0 
        else:
            hp = desktop.height()-t.height()
        if position.find('right') != -1:
            wp = desktop.width()-t.width()
        else:
            wp = 0
    else:
        wp,hp = [int(i) for i in position.split(',')]
    w.move(wp,hp)
    w.show()
    timer = QTimer()
    timer.timeout.connect(update_img)
    #10 minitues
    timer.start(1000*60*10)
    sys.exit(app.exec_())

@click.command()
@click.option('--inputfile','-i',default='',help='输入文件（.csv | .xls | .xlsx）')
@click.option('--outputfile','-o',default='',help='输出文件(.jpg | .png)')
@click.option('--demo','-d',default=False,help='输出一个demo.csv',is_flag=True)
@click.option('--color','-c',default='tomato,wheat',help='设置颜色(matplotlib)')
@click.option('--width','-w',default=9,help='条形块的宽度')
@click.option('--gap','-g',default=4,help='条形块之间的间隔')
@click.option('--figsize','-f',default='10,6',help='输出图片大小，默认（10，6）')
@click.option('--font_file',default='',help='设置字体文件')
@click.option('--display',default=False,help='在桌面上显示甘特图',is_flag=True)
@click.option('--opacity',default=0.85,help='透明度')
@click.option('--position','-p',default='topright',help='窗口显示位置')
@click.option('--title_bar','-t',default=False,help='窗口显示位置',is_flag=True)
def main(inputfile,outputfile,demo,color,width,gap,figsize,font_file,display,opacity,title_bar,position):
    delete_temp = False
    if inputfile:
        if display and not outputfile:
            outputfile = 'temp__s.jpg'
            delete_temp = True
        color = color.split(',')
        figsize = tuple([int(i) for i in figsize.split(',')])
        Gantt(inputfile,color,width,gap,font_file,outputfile,figsize)
        gantt_params = inputfile,color,width,gap,font_file,outputfile,figsize
        if not outputfile:
            plt.show()
    if demo:
        csv = '''任务名称,开始日期,持续天数
任务 1,11月7日,10
任务 2,11月10日,8
任务 3,11月7日,5'''
        open('demo.csv','w').write(csv)
    if display:
        display_gantt_on_desktop(outputfile,opacity,position,title_bar,delete_temp,gantt_params)

if __name__=='__main__':
    main()