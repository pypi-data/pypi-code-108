import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

from numpy.core.fromnumeric import size

class ManualInputTopLevel(tk.Toplevel):
    def __init__(self,supportList):
        tk.Toplevel.__init__(self)
        self.supportedList = supportList
        self.title("Manual Input Dialog")
        # sets the geometry of toplevel
        self.geometry("600x300")

        tk.Frame.rowconfigure(self,0,weight=1)
        tk.Frame.columnconfigure(self,0,weight=4)
        tk.Frame.columnconfigure(self,1,weight=3)

        #Left side Frame for input
        leftFrame = tk.Frame(master=self,background="#808080")
        leftFrame.grid(row=0,column=0,sticky='nsew')
        leftFrame.grid_propagate(False)

        companyLable = tk.Label(leftFrame,text="Company",font=("Arial", 15))
        companyLable.grid(column=0,row=0,sticky='ns')
        companyLable.grid_propagate(False)


        self.selectedCompany = tk.StringVar(leftFrame)
        self.selectedCompany.set(self.supportedList[0]) # default value
        self.companyDropdown = tk.OptionMenu(leftFrame,self.selectedCompany,*self.supportedList)
        self.companyDropdown.grid(column=1,row=0,sticky='nwse',padx=5,pady=5)

        policyLable = tk.Label(leftFrame,text="Policy No.",font=("Arial", 15))
        policyLable.grid(column=0,row=1,sticky='ns',padx=5,pady=5)
        policyLable.grid_propagate(False)

        self.policyTextField = tk.Entry(leftFrame,font=("Arial", 10),width=20)
        self.policyTextField.grid(column=1,row=1,sticky='nwse',padx=5,pady=5)
        self.policyTextField.grid_propagate(False)

        addButton = tk.Button(leftFrame,text="ADD POLICY",command=self.__addPolicy)
        returnButton = tk.Button(leftFrame,text="CONFIRM AND RETURN",command=self.__confirmReturn)
        addButton.grid(row=2,column=0, sticky='nsew',padx=5, pady=5)
        returnButton.grid(row=2,column=1, sticky='nsew',padx=5, pady=5)


        #Right side Frame for display list
        rightFrame = tk.Frame(master=self)
        tk.Frame.rowconfigure(rightFrame,0,weight=1)
        tk.Frame.columnconfigure(rightFrame,0,weight=1)
        rightFrame.grid(row=0,column=1,sticky='nsew')
        rightFrame.grid_propagate(False)


        self.policyListView = ttk.Treeview(rightFrame,show='headings')
        self.policyListView.bind("<Double-1>", self.__OnDoubleClick)
        self.policyListView["column"]=('Company', 'PolicyNo')
        self.policyListView.grid(row=0,column=0,rowspan=2,sticky='nsew')
        col_width = self.policyListView.winfo_width()
        self.policyListView.column("Company",width=col_width)
        self.policyListView.column("PolicyNo",width=col_width)
        self.policyListView.heading("Company",text="Company")
        self.policyListView.heading("PolicyNo",text="Policy No.")


        #Init variable
        self.policyDataList = []

    def show(self):
        self.wait_window()
        return self.policyDataList
    
    def __addPolicy(self):
        print(self.selectedCompany.get())
        print(self.policyTextField.get())

        if self.policyTextField.get() == None or self.policyTextField.get() == "":
            messagebox.showerror("Error", "Please input Policy")
        else:
            singleDataNode = [self.selectedCompany.get(),self.policyTextField.get()]
            #self.policyDataList.append(singleDataNode)
            self.policyListView.insert('','end',values=singleDataNode)
        
        self.policyTextField.delete(0, 'end')
    
    def __OnDoubleClick(self,event):
        item = self.policyListView.selection()[0]
        self.policyListView.delete(item)

    def __confirmReturn(self):
        for line in self.policyListView.get_children():                
            data = self.policyListView.item(line,'values')
            self.policyDataList.append(data)
        
        self.destroy()
        