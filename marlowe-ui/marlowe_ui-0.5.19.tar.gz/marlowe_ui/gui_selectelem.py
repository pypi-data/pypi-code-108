import tkinter as tk

from .physics import element as elem

# coloring taken from wikipedia
buttoncolors = {
        'AM':'#ff6666', # Alkali metals
        'EM':'#ffdead', # Alkaline earth metals
        'LA':'#ffbfff', # Lantanoides
        'AC':'#ff99cc', # Actinoides
        'TM':'#ffc0c0', # Transition metals
        'PM':'#cccccc', # Post-transition metals
        'MD':'#cccc99', # Mettalloids
        'NM':'#a0ffa0', # Other nonmetals
        'HL':'#ffff99', # Halogens
        'NB':'#c0ffff', # Noble gases
        'UN':'#e8e8e8', # Unknown chemical properties
        }

buttonlayout = {
    # p1
    'H':(0, 0, 'NM'), 'He':(0, 17, 'NB'),
    # p2
    'Li':(1, 0, 'AM'), 'Be':(1, 1, 'EM'), 'B':(1, 12, 'MD'), 'C':(1, 13, 'NM'),
    'N':(1, 14, 'NM'), 'O':(1, 15, 'NM'), 'F':(1, 16, 'HL'), 'Ne':(1, 17, 'NB'),
    # p3
    'Na':(2, 0, 'AM'), 'Mg':(2, 1, 'EM'), 'Al':(2, 12, 'PM'), 'Si':(2, 13, 'MD'),
    'P':(2, 14, 'NM'), 'S':(2, 15, 'NM'), 'Cl':(2, 16, 'HL'), 'Ar':(2, 17, 'NB'),
    # p4
    'K':(3,0,'AM'), 'Ca':(3,1,'EM'), 'Sc':(3,2,'TM'), 'Ti':(3,3,'TM'),
    'V':(3,4,'TM'), 'Cr':(3,5,'TM'), 'Mn':(3,6,'TM'), 'Fe':(3,7,'TM'),
    'Co':(3,8,'TM'), 'Ni':(3,9,'TM'), 'Cu':(3,10,'TM'), 'Zn':(3,11,'TM'),
    'Ga':(3,12,'PM'), 'Ge':(3,13,'MD'), 'As':(3,14,'MD'), 'Se':(3,15,'NM'),
    'Br':(3,16,'HL'), 'Kr':(3,17,'NB'),
    # p5
    'Rb':(4,0,'AM'), 'Sr':(4,1,'EM'), 'Y':(4,2,'TM'), 'Zr':(4,3,'TM'),
    'Nb':(4,4,'TM'), 'Mo':(4,5,'TM'), 'Tc':(4,6,'TM'), 'Ru':(4,7,'TM'),
    'Rh':(4,8,'TM'), 'Pd':(4,9,'TM'), 'Ag':(4,10,'TM'), 'Cd':(4,11,'TM'),
    'In':(4,12,'PM'), 'Sn':(4,13,'PM'), 'Sb':(4,14,'MD'), 'Te':(4,15,'MD'),
    'I':(4,16,'HL'), 'Xe':(4,17,'NB'),
    # p6 except Lantanoides
    'Cs':(5,0,'AM'), 'Ba':(5,1,'EM'), '__La__':(5,2,'LA'), 'Hf':(5,3,'TM'),
    'Ta':(5,4,'TM'), 'W':(5,5,'TM'), 'Re':(5,6,'TM'), 'Os':(5,7,'TM'),
    'Ir':(5,8,'TM'), 'Pt':(5,9,'TM'), 'Au':(5,10,'TM'), 'Hg':(5,11,'TM'),
    'Tl':(5,12,'PM'), 'Pb':(5,13,'PM'), 'Bi':(5,14,'PM'), 'Po':(5,15,'PM'),
    'At':(5,16,'HL'), 'Rn':(5,17,'NB'),
    # p7 except Actinodes
    'Fr':(6,0,'AM'), 'Ra':(6,1,'EM'), '__Ac__':(6,2,'AC'), 'Rf':(6,3,'TM'),
    'Db':(6,4,'TM'), 'Sg':(6,5,'TM'), 'Bh':(6,6,'TM'), 'Hs':(6,7,'TM'),
    'Mt':(6,8,'UN'), 'Ds':(6,9,'UN'), 'Rg':(6,10,'UN'), 'Cn':(6,11,'TM'),
    'Uut':(6,12,'UN'), 'Fl':(6,13,'UN'), 'Uup':(6,14,'UN'), 'Lv':(6,15,'UN'),
    'Uus':(6,16,'UN'), 'Uuo':(6,17,'UN'),
    # Lantannoides 
    'La':(7,2,'LA'),
    'Ce':(7,3,'LA'), 'Pr':(7,4,'LA'), 'Nd':(7,5,'LA'), 'Pm':(7,6,'LA'),
    'Sm':(7,7,'LA'), 'Eu':(7,8,'LA'), 'Gd':(7,9,'LA'), 'Tb':(7,10,'LA'),
    'Dy':(7,11,'LA'), 'Ho':(7,12,'LA'), 'Er':(7,13,'LA'), 'Tm':(7,14,'LA'),
    'Yb':(7,15,'LA'), 'Lu':(7,16,'LA'),
    # Actinoides
    'Ac':(8,2,'AC'),
    'Th':(8,3,'AC'), 'Pa':(8,4,'AC'), 'U':(8,5,'AC'), 'Np':(8,6,'AC'),
    'Pu':(8,7,'AC'), 'Am':(8,8,'AC'), 'Cm':(8,9,'AC'), 'Bk':(8,10,'AC'),
    'Cf':(8,11,'AC'), 'Es':(8,12,'AC'), 'Fm':(8,13,'AC'), 'Md':(8,14,'AC'),
    'No':(8,15,'AC'), 'Lr':(8,16,'AC')}

class SelectElem(tk.Frame):
    """
    """
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        #self.pack()

        # reserve results when this dialog is closed
        self.how = None

        for e in elem.table_bynum[1:]:
            text = '{0.z:d}\n{0.sym:s}'.format(e)
            row, col, colortype = buttonlayout[e.sym]
            bgcolor = buttoncolors[colortype]
            btn = tk.Button(self, text=text, width=4,
                    background=bgcolor,
                    command=self.skel_pushcmd(e.z))
            if row > 6:
                row += 1
            btn.grid(row=row,column=col,padx=1,pady=1)
        # put space between regular and La, Ac series
        tk.Frame(self,height=5).grid(row=7,column=0, columnspan=17)

        # put tiles to fill La and Ac
        row, col, colortype = buttonlayout['__La__']
        latile = tk.Label(self, background=buttoncolors['LA'])
        latile.grid(row=row,column=col,padx=1,pady=1,
                sticky=tk.W+tk.E+tk.N+tk.S)
        row, col, colortype = buttonlayout['__Ac__']
        actile = tk.Label(self, background=buttoncolors['AC'])
        actile.grid(row=row,column=col,padx=1,pady=1,
                sticky=tk.W+tk.E+tk.N+tk.S)



        # cancel button
        tk.Frame(self,height=5).grid(row=11,column=0, columnspan=17)
        tk.Button(self, text='cancel', command=self.cancel_command)\
                .grid(row=12, column=16, columnspan=2)


    def skel_pushcmd(self, z):
        def pushcmd():
            self.how = elem.table_bynum[z]
            self.master.destroy()
        return pushcmd

    def cancel_command(self):
        self.master.destroy()

if __name__ == '__main__':
    app = tk.Tk()

    name = tk.StringVar(app)
    sym = tk.StringVar(app)
    z = tk.DoubleVar(app)
    mass = tk.DoubleVar(app)

    nameent = tk.Entry(app, textvariable=name)
    nameent.pack()
    syment = tk.Entry(app, textvariable=sym)
    syment.pack()
    zent = tk.Entry(app, textvariable=z)
    zent.pack()
    massent = tk.Entry(app, textvariable=mass)
    massent.pack()

    def btn_action():
        win = tk.Toplevel()
        se = SelectElem(win)
        se.pack()
        win.focus_set()
        win.grab_set()
        win.wait_window()

        if se.how:
            name.set(se.how.name)
            sym.set(se.how.sym)
            z.set(se.how.z)
            mass.set(se.how.mass)

    tk.Button(app, text='pop', command=btn_action).pack()

    app.mainloop()
