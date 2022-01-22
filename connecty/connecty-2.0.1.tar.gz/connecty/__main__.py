import tkinter.filedialog
from configparser import ConfigParser
import connecty
from tkinter import *
from tkinter import ttk, messagebox
import colorama
from importlib import resources
colorama.init()

CBLUE = "\33[34m"
CVIOLET = "\33[35m"
CEND = "\033[0m"
CBOLD = "\033[1m"

def wrap(cl):
    def fu(txt):
        return cl + txt + CEND
    return fu

print(wrap(CBLUE)("▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"))
print(wrap(CBLUE)("▉") + CBOLD + " JOIN THE SUPPORT SERVER FOR HELP!! https://discord.gg/fcZBB2v " + wrap(CBLUE)("█"))
print(wrap(CBLUE)("█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█"))

connections = {}
args = connecty.parser.parse_args()
bot = connecty.Bot()
connecty.GB.bot = bot
active_file = None
root = Tk()
root.title("Connecty")
frame = ttk.Frame(root, padding="10 10 10 10")
# get window size
w = 600
h = 190
# constrain size
root.minsize(width=w, height=h)
root.maxsize(width=w, height=h)
frame.grid(column=0, row=0, sticky=(N, W, E, S))
con_selection = StringVar()
cha_selection = StringVar()
token = StringVar(value="<Token>")

def load_config(file):
    global bot_config, connections, active_file
    active_file = file
    config = ConfigParser()
    config.read_string(resources.read_text(connecty, "defaults.ini"))
    config.read(file)
    token.set(config["BOT"]["token"])
    del config["BOT"]
    connections = {sec: [int(id) for id in config[sec]["channels"].split()] for sec in config.sections()}
    async def init():
        for con in connections.values():
            await bot.register(con)
    bot.startup = init

def save_config(confile):
    config = ConfigParser()
    config["BOT"] = {"token": token.get()}
    for con in connections:
        config[con] = {"channels": " ".join(str(id) for id in connections[con])}
    with open(confile, "w") as f:
        config.write(f)

def start():
    root.destroy()
    bot.run(token.get())

if str(args.config) != 'default':
    load_config(args.config)
    if not args.I:
        start()

con_inp = ttk.Entry(frame, textvariable=con_selection)
con_inp.grid(column=0, row=1)

con_combo = ttk.Combobox(frame, values=list(connections.keys()), state="readonly")
con_combo.grid(column=1, row=1)
def fun_con_combo(*args):
    con_selection.set(con_combo.get())
    update()
con_combo.bind("<<ComboboxSelected>>", fun_con_combo)

def fun_con_add(*args):
    if not verify(): return
    connections[con_selection.get()] = []
    update()
con_add = ttk.Button(frame, text="Add", command=fun_con_add)
con_add.grid(column=0, row=0, sticky=(W, E))

def fun_con_rem(*args):
    if not verify(): return
    del connections[con_selection.get()]
    con_selection.set('')
    update()
con_rem = ttk.Button(frame, text="Remove", command=fun_con_rem)
con_rem.grid(column=1, row=0, sticky=(W, E))


cha_inp = ttk.Entry(frame, textvariable=cha_selection)
cha_inp.grid(column=2, row=1)

cha_combo = ttk.Combobox(frame, values=[], state="readonly")
def fun_cha_combo(*args):
    cha_selection.set(cha_combo.get())
    update()
cha_combo.grid(column=3, row=1)
cha_combo.bind("<<ComboboxSelected>>", fun_cha_combo)

def fun_cha_add(*args):
    if not verify() or cha_selection.get() == '': return
    connections[con_selection.get()].append(int(cha_selection.get()))
    update()
cha_add = ttk.Button(frame, text="Add", command=fun_cha_add)
cha_add.grid(column=2, row=0, sticky=(W, E))

def fun_cha_rem(*args):
    if not verify() or cha_selection.get() == '': return
    connections[con_selection.get()].remove(int(cha_selection.get()))
    cha_selection.set('')
    update()
cha_rem = ttk.Button(frame, text="Remove", command=fun_cha_rem)
cha_rem.grid(column=3, row=0, sticky=(W, E))


ttk.Label(frame, text="").\
    grid(column=0, row=2)

def open_file(*args):
    file = tkinter.filedialog.askopenfilename(initialdir=".")
    if file == '': return
    con_selection.set('')
    cha_selection.set('')
    load_config(file)
    update()
ttk.Button(frame, text="Load", command=open_file).\
    grid(column=0, row=3, sticky=(W, E))

def new_file(*args):
    global active_file
    file = tkinter.filedialog.asksaveasfilename(initialdir=".")
    if file == '': return
    with open(file, "w") as f: f.write("")
    connections.clear()
    con_selection.set('')
    cha_selection.set('')
    token.set('')
    active_file = file
    update()
ttk.Button(frame, text="New", command=new_file).\
    grid(column=1, row=3, sticky=(W, E))

ttk.Entry(frame, textvariable=token).\
    grid(column=2, row=3, columnspan=2, sticky=(W, E))


def begin_bot(*args):
    if len(token.get()) != 59:
        messagebox.showerror("Error", "Invalid token - must be 59 characters long")
        return
    if not active_file:
        messagebox.showerror("Error", "No file loaded - press 'New' or 'Load' first")
        return
    save_config(active_file)
    start()
Button(frame, text="Run", bg='#8CEFFF', command=begin_bot).\
    grid(column=0, row=4, columnspan=4, sticky=(W, E))


def verify():
    if con_selection.get() == '':
        return False
    if " " in con_selection.get():
        con_selection.set('')
        messagebox.showerror("Error", "No spaces in name")
        return False
    if not (cha_selection.get().isnumeric() or cha_selection.get() == ""):
        cha_selection.set('')
        messagebox.showerror("Error", "Numbers only in channel")
        return False
    return True

def update():
    if not con_selection.get():
        con_combo.set('')
        con_selection.set('')
        cha_combo.set('')
        cha_combo.config(values=[])
    else:
        con_combo.set(con_selection.get())
        con_selection.set(value=con_selection.get())
        cha_combo.config(values=connections[con_selection.get()])
    if not cha_selection.get():
        cha_combo.set('')
        cha_selection.set(value='')
    else:
        cha_combo.set(cha_selection.get())
        cha_selection.set(value=cha_selection.get())
    con_combo.config(values=list(connections.keys()))

for child in frame.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()
if __name__ == "__main__":
    pass


