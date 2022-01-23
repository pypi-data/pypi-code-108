"""Make your tkinter wedgets responsive"""
# https://www.w3schools.com/html/html_responsive.asp
class Responsive():
    def __init__(self,master,value,orient='horizontal'):
        """
        Modify your widget depending on the max size of the parent

        Attributes
        ---
        `master` - The root window ( Tk )

        `value` - The size of the window

        `orient` - The orentation: horizontal (width), vertical (height)
        
        """
        self.default = []
        self.master = []
        self.kw = []
        def resize(e):
            root.title('Window Title %sx%s'%( str(root.winfo_width()), str(root.winfo_height()) ))

            if orient=='horizontal':
                ops=root.winfo_width()
            elif orient=='vertical':
                ops=root.winfo_height()
            else:
                ops = 100

            if ops >= value:
                count=0
                for i in self.master:
                    i.grid(**self.kw[count])
                    count+=1
            else:
                count=0
                for i in self.master:
                    i.grid(**self.default[count])
                    count+=1
        master.bind('<Configure>', resize)
        
    def grid(self,master,**kw):
        """
        Modify the grid geometry

        Attributes
        ---
        `master` - The widget to update the grid.

        `kw` - The grid properties to apply.
        """
        self.master.append(master)
        self.kw.append(kw)
        self.default.append(master.grid_info())

    # Planned functions
    # def place(self,master,**kw):
    #     """Modify the place geometry"""
    #     print('Feature not added yet!')
    # def pack(self,master,**kw):
    #     """Modify the pack geometry"""
    #     print('Feature not added yet!')
    # def config(self,master,**kw):
    #     """Modify the wedget"""
    #     print('Feature not added yet!')

if __name__ == '__main__':

    from tkinter import Frame, Tk
    root=Tk()
    root.title('Window Title')
    # root.minsize(356,346)
    root.geometry('900x900')

    # resize the window to see that the three Frames below will display horizontally on large screens and stacked vertically on small screens:
    left = Frame(root,width=300,height=300,bg='blue')
    left.grid(row=0,column=0)
    main = Frame(root,width=300,height=300,bg='gray')
    main.grid(row=1,column=0)
    right = Frame(root,width=300,height=300,bg='green')
    right.grid(row=2,column=0)

    # Make widgets responsive
    R = Responsive(root,901)
    R.grid(main,row=0,column=1)
    R.grid(right,row=0,column=2)

    root.mainloop()