"""
Image Viewer for nhentaidevs.

author : JohnLesterDev
"""

# Packages
import os
import sys

from tkinter import *
from tqdm import tqdm
from PIL import Image
from PIL import ImageTk
from random import choice
from tkinter import filedialog
from click import command, argument


# Path constant
path = os.getcwd()


# Tkinter Constructor


src = Tk()
src.title("PLEASE WAIT..... :>")
src.geometry("144x44")
src.configure(bg="black")


# Pillow image list generator from a given source
def img_generate(source) -> list:
    global src
    
    ls_one = []
    ls_two = []
    ls_three = []
    files = os.listdir(str(source))[:-1]
    print("\n")

    l = Label(src, text="Please Wait.... :>", bg="black", fg="white")
    l.pack()
    
    for file in tqdm(files, unit=" img", colour="green"):
        img = Image.open("{}/{}".format(str(source), file))
        width, height = img.size
        img = img.resize(((width//3)+85, (height//3)+85))

        tk_img = ImageTk.PhotoImage(img)

        ls_ = list(str(file).split('.')[0])
        if len(ls_) == 2:
            ls_two.append([tk_img, (width//2)+85, (height//3)+85, file])
        elif len(ls_) == 3:
            ls_three.append([tk_img, (width//2)+85, (height//3)+85, file])
        else:
            ls_one.append([tk_img, (width//2)+85, (height//3)+85, file])

    l.destroy()

    return ls_one+ls_two+ls_three


@command()
@argument('code', required=False)
def commander(code):
    if code == "random":
        codes = []
        for file in os.listdir(os.getcwd()):
            if str(file).isdigit():
                codes.append(file)

        code = choice(codes)
    
    # Globals
    global ent
    global src
    global path
    global label
    global b_for
    global b_bac
    global b_selc
    global images
    global temp_one
    global temp_two

    path = os.path.join(path, str(code))


    def forward(num):
        global path
        global src
        global label
        global b_for
        global b_bac
        global b_selc
        global images

        for widget in [label, b_for, b_bac, b_selc]:
            widget.forget()

        label = Label(src, image=images[num-1][0])
        b_for = Button(
            src,
            fg="white",
            bg="black",
            text=">>>",
            activebackground="black",
            activeforeground="white",
            command=lambda: forward(num+1))
        b_selc = Button(src, text="Open New...")
        b_bac = Button(
            src,
            fg="white",
            bg="black",
            text="<<<",
            activebackground="black",
            activeforeground="white",
            command=lambda: back(num-1))

        offset = images[num-1][2]//4

        if num == len(images):
            label.pack(side="left")
            b_bac.pack(ipadx=11, ipady=offset, fill='x')
        else:
            label.pack(side="left")
            b_for.pack(ipadx=11, ipady=offset, fill='x')
            b_bac.pack(ipadx=11, ipady=offset, fill='x')

        src.title("Doujin Seeker - {0}".format(
            os.path.join(path, images[num-1][3])))
        src.geometry("{}x{}".format(images[num-1][1], images[num-1][2]))
        


    def back(num):
        global path
        global src
        global label
        global b_for
        global b_bac
        global b_selc
        global images

        for widget in [label, b_for, b_bac, b_selc]:
            widget.forget()

        label = Label(src, image=images[num-1][0])
        b_for = Button(
            src,
            fg="white",
            bg="black",
            text=">>>",
            activebackground="black",
            activeforeground="white",
            command=lambda: forward(num+1))
        b_selc = Button(src, text="Open New...")
        b_bac = Button(
            src,
            fg="white",
            bg="black",
            text="<<<",
            activebackground="black",
            activeforeground="white",
            command=lambda: back(num-1))

        offset = images[num-1][2]//4
    
        if num == 1:
            label.pack(side="left")
            b_for.pack(ipadx=11, ipady=offset, fill='x')
        else:
            label.pack(side="left")
            b_for.pack(ipadx=11, ipady=offset, fill='x')
            b_bac.pack(ipadx=11, ipady=offset, fill='x')

        src.title("Doujin Seeker - {0}".format(
            os.path.join(path, images[num-1][3])))
        src.geometry("{}x{}".format(images[num-1][1], images[num-1][2]))

    # Image Folder used as a list
    
    if code:
        images = img_generate(str(code))
    else:
        path = filedialog.askdirectory(initialdir=os.getcwd())
        if path:
            images = img_generate(path)
        else:
            src.quit()
            return
        
    

    # Widgets    
    label = Label(src, image=images[0][0])
    b_for = Button(
        src,
        fg="white",
        bg="black",
        text=">>>",
        activebackground="black",
        activeforeground="white",
        command=lambda: forward(2))
    b_selc = Button(src, text="Open New...")
    b_bac = Button(
        src,
        fg="white",
        bg="black",
        text="<<<",
        state=DISABLED,
        activebackground="black",
        activeforeground="white") 

    # Packing
    offset = images[0][2]//4
    
    label.pack(side="left")
    b_for.pack(ipadx=11, ipady=offset, fill='x')

    # Modifying the window
    src.title("Doujin Seeker - {0}".format(
        os.path.join(path, images[0][3])))
    src.geometry("{}x{}".format(images[0][1], images[0][2]))
    src.mainloop()


if __name__ == "__main__":
    commander()

