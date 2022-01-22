import tkinter as tk
from tkinter import ttk

class RunningStatusFrame(tk.Frame):
    def __init__(self,masterFrame,col_idx,company):
        super().__init__(masterFrame)
        self.grid_propagate(0)
        self.grid(row=0,column=col_idx,sticky='nwes',padx=5, pady=5)
        #row 0 = list box, row 1 = running status
        tk.Frame.rowconfigure(self,0,weight=15)
        tk.Frame.rowconfigure(self,1,weight=1)
        tk.Frame.rowconfigure(self,2,weight=1)
        tk.Frame.columnconfigure(self,0,weight=1)

        #create list box
        self.listbox = tk.Listbox(self,listvariable=tk.StringVar(value=company))
        self.listbox.grid(column=0,row=0,sticky='nwes')

        # link a scrollbar to a list
        scrollbar = tk.Scrollbar(
            self,
            orient='vertical',
            command=self.listbox.yview
        )

        self.listbox['yscrollcommand'] = scrollbar.set

        scrollbar.grid(
            column=1,
            row=0,
            sticky='ns')

        
        #create status lable
        self.statusText=tk.StringVar()
        self.statusText.set("Waiting Execute")

        self.statusLable = tk.Label(self,textvariable=self.statusText)
        self.statusLable.grid(column=0,row=2,columnspan=2,sticky='nwes')
        self.statusLable.grid_propagate(False)

        #create Progress bar
        self.progressValue = 0
        self.progressBar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            maximum= (len(company)-1) * 2
            #time 2 is scrap and build
        )
        # place the progressbar
        self.progressBar.grid(column=0, row=1, columnspan=2, padx=5,pady=5,sticky='we')
        self.progressBar.grid_propagate(False)

    def setStatusLableText(self,text):
        self.statusText.set(text)

    def setStatusProgresValueByValue(self,value):
        self.progressValue = self.progressValue+value
        self.progressBar["value"] = self.progressValue

    def resetProgress(self):
        self.progressValue = 0
        self.progressBar["value"] = self.progressValue
        self.statusText.set('Waiting Execute')
