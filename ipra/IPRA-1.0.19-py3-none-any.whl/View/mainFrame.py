from ipra.Controller.reportThreadController import ReportThreadController
from ipra.Controller.robotThreadController import RobotThreadController
from ipra.Controller.policyCollectionController import PolicyCollectionController
from ipra.Utility.tkinterUtility import *
from ipra.Logger.logger import Logger
from ipra.View.runningStatusFrame import RunningStatusFrame
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from ipra.View.manualInputTopLevel import ManualInputTopLevel
from ipra.View.editSettingTopLevel import EditSettingTopLevel



class MainApplication(tk.Tk):
    frame_running_state = None
    frame_instances_running_state = []
    __VERSION = "1.0.19"
    __DATE = "21-JAN-2022"

    def __init__(self):
        tk.Tk.__init__(self)
        #tk.Frame.__init__(self,parent,*args,**kwargs)
        #self.parent = parent
        self.logger = Logger()
        self.logger.writeLogString('MAINFRAME','START IPRA {0}'.format(self.__VERSION))
        self.title("IPRA v.{0}".format(self.__VERSION))
        self.geometry("500x700")
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", self.__closeMainFrame)
        self.__createMenuBar()
        
        tk.Frame.rowconfigure(self.main_frame,0,weight=1)
        tk.Frame.rowconfigure(self.main_frame,1,weight=10)
        tk.Frame.rowconfigure(self.main_frame,2,weight=1)
        tk.Frame.columnconfigure(self.main_frame,0,weight=1)

        #Open excel, work sheet etc. prepare all the policy no.
        frame_open_excel = tk.Frame(master=self.main_frame)
        frame_open_excel.grid(row=0,column=0,sticky='nsew')
        frame_open_excel.grid_propagate(0)

        #Display Policy no. and running status
        self.frame_running_state = tk.Frame(master=self.main_frame,background="#808080")
        self.frame_running_state.grid(row=1,column=0,sticky='nsew')
        self.frame_running_state.grid_propagate(0)
        
        #start/clean running state
        frame_exeRobot = tk.Frame(master=self.main_frame)
        frame_exeRobot.grid(row=2,column=0,sticky='nsew')
        frame_exeRobot.grid_propagate(0)

        self.__createFrameOpenExcel(frame_open_excel)
        self.__createFrameExeRobot(frame_exeRobot)
        
        
        self.policyController = PolicyCollectionController()
        self.robotThreadController = RobotThreadController()
        self.reportThreadController = ReportThreadController()
        
    def startFrame(self):
        self.mainloop()
    
    def __createMenuBar(self):
        menubar = Menu(self, background='#ff8000', foreground='black', activebackground='white', activeforeground='black')  

        edit = Menu(menubar, tearoff=0)  
        edit.add_command(label="Edit Setting", command=self.__editSetting)  
        menubar.add_cascade(label="Setting", menu=edit)  

        help = Menu(menubar, tearoff=0)  
        help.add_command(label="About", command=self.__about)  
        menubar.add_cascade(label="Help", menu=help)
        
        self.config(menu=menubar)
    
    def __about(self):
        aboutWindow = Toplevel(self)
        aboutWindow.iconbitmap('C:\IPRA\RESOURCE\hexicon.ico')
        aboutWindow.title("About")
 
        # sets the geometry of toplevel
        aboutWindow.geometry("300x350")

        # A Label widget to show in toplevel
        version = Label(aboutWindow,text ="Version:{0}".format(self.__VERSION))
        version.config(font=('bold',15))
        version.pack(anchor=NW)
        date = Label(aboutWindow,text ="RELEASE DATE:{0}".format(self.__DATE))
        date.config(font=('bold',15))
        date.pack(anchor=NW)
        Label(aboutWindow,text ="")

        # A Label widget to show in toplevel
        Label(aboutWindow,text ="Supported Below Insurance Company").pack()
        
        listbox_widget = Listbox(aboutWindow,height=50)
        for entry in self.policyController.getPolicyCollection():
            listbox_widget.insert(END, entry[0])
        listbox_widget.pack()
    
    def __editSetting(self):
        editSettingDialog = EditSettingTopLevel()
        editSettingDialog.show()
        return
        
    def __createFrameOpenExcel(self,frame):
        Grid.rowconfigure(frame,0,weight=1)
        Grid.columnconfigure(frame,0,weight=1)
        Grid.columnconfigure(frame,1,weight=1)

        button_standard = Button(frame, text ="Standard Policy No. List", command=self.__openStandardFile)
        button_manual = Button(frame,text ="Manual Input Policy No. List",command=self.__openManualInputDialog)

        button_standard.grid(row=0,column=0, sticky='nsew',padx=5, pady=5)
        button_manual.grid(row=0,column=1, sticky='nsew',padx=5, pady=5)
        return

    def __createFrameExeRobot(self,frame):
        Grid.rowconfigure(frame,0,weight=1)
        Grid.columnconfigure(frame,0,weight=1)
        Grid.columnconfigure(frame,1,weight=1)
        Grid.columnconfigure(frame,2,weight=1)

        button_reset = Button(frame, text ="RESET DATA",command = self.__cleanFrameRunningState)
        button_start = Button(frame,text ="START ROBOT",command=self.__startRobot)
        button_report = Button(frame,text ="BUILD REPORT ONLY",command=self.__buildReport)

        button_reset.grid(row=0,column=0, sticky='nsew',padx=5, pady=5)
        button_start.grid(row=0,column=1, sticky='nsew',padx=5, pady=5)
        button_report.grid(row=0,column=2, sticky='nsew',padx=5, pady=5)
        return

    def __openStandardFile(self):
        filePath = openFileAll()
        if filePath != None and filePath != '':
            readResult = self.policyController.getPolicyListFromFile(filePath)
            if readResult:
                self.__displaySearchPolicy()
            else:
                messagebox.showerror("Error", "Read File Error.\nPlease correct worksheet name or format")
        return
    
    def __openManualInputDialog(self):
        manualInputDialog = ManualInputTopLevel(self.policyController.getSupportedList())
        manualList = manualInputDialog.show()
        self.policyController.policySwitchByList(manualList)
        self.__displaySearchPolicy()
        return

    def __displaySearchPolicy(self):
        column_idx = 0
        Grid.rowconfigure(self.frame_running_state,0,weight=10)
        for company in self.policyController.getPolicyCollection():
            if(len(company)>1):
                Grid.columnconfigure(self.frame_running_state,column_idx,weight=1)
                frameTemp = RunningStatusFrame(self.frame_running_state,column_idx,company)
                column_idx = column_idx + 1
                self.frame_instances_running_state.append(frameTemp)
            else:
                self.frame_instances_running_state.append(None)

    def __cleanFrameRunningState(self):
        #Clean and reset
        
        for frame in self.frame_instances_running_state:
            if frame != None:
                frame.destroy()
        #self.frame_running_state.destory()
        self.__resetFrameRunningState()
        self.frame_instances_running_state = []
        self.policyController.cleanAllPolicy()

    def __startRobot(self):
        self.robotThreadController.createRobotThread(self.policyController.getPolicyCollection(),self.frame_instances_running_state)

    def __buildReport(self):
        self.reportThreadController.createReportThread(self.policyController.getPolicyCollection(),self.frame_instances_running_state)

    def __closeMainFrame(self):
        #Shut down all frame and close all webdriver
        #Important to release all resources
        self.robotThreadController.destoryAllRobotThread()
        self.destroy()

        return

    def __resetFrameRunningState(self):
        self.frame_running_state = tk.Frame(master=self.main_frame,background="#808080")
        self.frame_running_state.grid(row=1,column=0,sticky='nsew')
        self.frame_running_state.grid_propagate(0)        






