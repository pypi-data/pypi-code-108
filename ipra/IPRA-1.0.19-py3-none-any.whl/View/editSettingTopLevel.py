import tkinter as tk
from tkinter.constants import DISABLED
import tkinter.ttk as ttk
import configparser
from ipra.Utility.tkinterUtility import *

class EditSettingTopLevel(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.config_obj = configparser.ConfigParser()
        self.config_obj.read("C:\IPRA\config.ini")

        self.title("Edit Setting")
        # sets the geometry of toplevel
        self.geometry("500x200")
        tk.Frame.rowconfigure(self,0,weight=1)
        tk.Frame.columnconfigure(self,0,weight=1)
        
        mainFrame = tk.Frame(master=self,background='#808080')
        mainFrame.grid(row=0,column=0,sticky='nsew')
        mainFrame.grid_propagate(False)
        
        #Output Path related
        outputPathLable = tk.Label(mainFrame,text="Output Path",font=("Arial", 13))
        outputPathLable.grid(column=0,row=0,sticky='ns',padx=5,pady=5)
        outputPathLable.grid_propagate(False)

        self.outputPath = tk.StringVar(mainFrame,value=self.config_obj['report_path']['outputPath'])
        self.outputPathTextField = tk.Entry(mainFrame,font=("Arial", 10),width=30,textvariable=self.outputPath,state=DISABLED)
        self.outputPathTextField.grid(column=1,row=0,sticky='nwse',padx=5,pady=5)
        self.outputPathTextField.grid_propagate(False)
        
        setOutputPathButton = tk.Button(mainFrame,text="Select Directory",command=self.__selectOutPutDirectory)
        setOutputPathButton.grid(column=2,row=0, sticky='nsew',padx=5, pady=5)
        #Output Path related
        
        #Input Path related
        inputPathLable = tk.Label(mainFrame,text="Input Path",font=("Arial", 13))
        inputPathLable.grid(column=0,row=1,sticky='ns',padx=5,pady=5)
        inputPathLable.grid_propagate(False)

        self.inputPath = tk.StringVar(mainFrame,value='')
        self.inputPathTextField = tk.Entry(mainFrame,font=("Arial", 10),width=30,textvariable=self.inputPath,state=DISABLED)
        self.inputPathTextField.grid(column=1,row=1,sticky='nwse',padx=5,pady=5)
        self.inputPathTextField.grid_propagate(False)
        
        returnButton = tk.Button(mainFrame,text="Select Directory",command=self.__selectInputPutDirectory)
        returnButton.grid(column=2,row=1, sticky='nsew',padx=5, pady=5)
        #Input Path related        
        
        returnButton = tk.Button(mainFrame,text="SAVE AND RETURN",command=self.__confirmReturn)
        returnButton.grid(column=0,row=2, sticky='nsew',padx=5, pady=5)


        
    def show(self):
        self.wait_window()
        return
    
    def __confirmReturn(self):
        self.config_obj.set(section='report_path',option='outputPath',value=self.outputPath.get())
        self.config_obj.set(section='report_path',option='inputPath',value=self.inputPath.get())
        with open('C:\IPRA\config.ini', 'w') as configfile:
            self.config_obj.write(configfile)
        self.destroy()
        return
    
    def __selectOutPutDirectory(self):
        self.outputPath.set(selectPath())
        return

    def __selectInputPutDirectory(self):
        self.inputPath.set(selectPath()+'/')
        return