from hi_mail_download.py_hisense_mail import HiMailDownload
from tkinter import *
from tkinter import filedialog
import threading
import inspect
import ctypes
from time import sleep

def download_thread():
    global runningflag
    runningflag = 1
    td = HiMailDownload()
    td.download_file(e1.get(), e2.get(), e3.get(), v4.get())

def pageupdate_thread():
    sleep(1)
    global runningflag
    isalivetmp = 255
    isalive = 255
    while exitflag == 0:
        for line in threading.enumerate():
            if line.getName() == "download":
                isalive = 1
                break
            else:
                isalive = 0

        if isalivetmp != isalive:
            isalivetmp = isalive

            if isalive == 1:
                print("CHECK!!!")
                lab.grid(row=4, column=4, columnspan=4, padx=30, sticky=W)
                root.update()
            elif isalive == 0:
                runningflag = 0
                print("CLEAN")
                lab.grid_forget()
                root.update()

if __name__ == '__main__':
    root = Tk()

    root.title("海信PLM邮件")
    root.geometry("730x280")
    photo = PhotoImage(file="./picture/notice.png")
    Label(root,text='帐号 :').grid(row=0,column=0,padx=30,sticky=W) # 对Label内容进行 表格式 布局
    Label(root,text='密码 :').grid(row=1,column=0,padx=30,sticky=W)
    Label(root,text='文件夹 :').grid(row=2,column=0,padx=30,sticky=W)
    Label(root,image = photo).grid(row=0,column=4, padx=30, rowspan=8,columnspan=4, sticky=E)

    lab = Label(root, text='Please Wait...', font=("微软雅黑", 20), fg="red")

    v1=StringVar()    # 设置变量 .
    v2=StringVar()
    v3=StringVar()
    v4=IntVar()

    e1 = Entry(root,textvariable=v1)            # 用于储存 输入的内容
    e2 = Entry(root,textvariable=v2,show='*')
    e3 = Entry(root,textvariable=v3,width=30)
    e4 = Checkbutton(root, text='是否打开浏览器细节（debug）', variable=v4, padx=30)

    e1.grid(row=0,column=1,padx=10,pady=10,sticky=W)      # 进行表格式布局 .
    e2.grid(row=1,column=1,padx=10,pady=10,sticky=W)
    e3.grid(row=2,column=1,padx=10,pady=10)
    e4.grid(row=3, column=0, columnspan=2, padx=10,pady=10,sticky=W)

    runningflag = 0
    exitflag = 0

    def showdirpath():
        root1 = Tk()
        root1.withdraw()
        file_path = filedialog.askdirectory()
        e3.delete(0, END)
        e3.insert(0, file_path)


    def _async_raise(tid, exctype):
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

    def quitmain():
        global exitflag
        exitflag = 1

        for line in threading.enumerate():
            if line.getName() == "download":
                _async_raise(line.ident, SystemExit)

        root.quit()

    def startdownload():
        try:
            downloadThread = threading.Thread(target=download_thread,)
            downloadThread.setName("download")
            if runningflag == 1:
                print("running")
            else:
                downloadThread.start()
        except:
            print("Error: 无法启动线程")

    #初始化

    usermessage=""
    passwordmessage=""
    pathmessage=""

    with open("login.txt", 'r') as f:
        for line in f.readlines():
            if "user:" in line:
                strlist=line.split("user:")
                usermessage=strlist[1]

            elif "password:" in line:
                strlist=line.split("password:")
                passwordmessage=strlist[1]

            elif "path:" in line:
                strlist=line.split("path:")
                pathmessage=strlist[1]

        f.close()


    e1.insert(0, "hscvte")
    e2.insert(0, "Hisense123")
    e3.insert(0, pathmessage)


    Button(root,text='开始',width=10,command=startdownload).grid(row=4,column=0,sticky=E,padx=10,pady=10)
    Button(root,text='退出',width=10,command=quitmain).grid(row=4,column=1,sticky=E,padx=10,pady=10)
    Button(root,text='...',width=7,command=showdirpath).grid(row=2,column=2,sticky=W,padx=10,pady=5)

    pageupdateThread = threading.Thread(target=pageupdate_thread, )
    pageupdateThread.start()

    mainloop()