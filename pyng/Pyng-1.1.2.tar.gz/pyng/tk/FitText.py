import Tkinter as tk

class MyFrame(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)

        root = self.master
        root.title("My Window Title")

        # Pack Frame into root window and make it expand in "both" x and y
        self.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        # Statistical weight of 1 = 100% for cell (0, 0) to expand 100%
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # The string text
        text = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed
diam nonummy nibh euismod tincidunt ut laoreet dolore magna
aliquam erat volutpat. Ut wisi enim ad minim veniam, quis
nostrud exerci tation ullamcorper suscipit lobortis nisl ut
aliquip ex ea commodo consequat. Duis autem vel eum iriure
dolor in hendrerit in vulputate velit esse molestie consequat,
vel illum dolore eu feugiat nulla facilisis at vero eros et
accumsan et iusto odio dignissim qui blandit praesent luptatum
zzril delenit augue duis dolore te feugait nulla facilisi. Nam
liber tempor cum soluta nobis eleifend option congue nihil
imperdiet doming id quod mazim placerat facer possim assum.
Typi non habent claritatem insitam; est usus legentis in iis qui
facit eorum claritatem. Investigationes demonstraverunt lectores
legere me lius quod ii legunt saepius. Claritas est etiam
processus dynamicus, qui sequitur mutationem consuetudium
lectorum. Mirum est notare quam littera gothica, quam nunc
putamus parum claram, anteposuerit litterarum formas
humanitatis per seacula quarta decima et quinta decima. Eodem
modo typi, qui nunc nobis videntur parum clari, fiant sollemnes
in futurum."""

        # Add a tk.Text widget to Frame (self) and its configuration
        textwidget = tk.Text(self, wrap="none", font=("Comic Sans MS", 12),
                             padx=10, pady=10)
        textwidget.grid(row=0, column=0, sticky="nesw")
        # Add the text to textwidget and disable editing
        textwidget.insert(tk.END, text)
        textwidget.config(state=tk.DISABLED)

        # Here is where the HACK begins
        def is_scroll(wh, lower, upper):
            # nonlocal size # apparently matters for Python 3?
            size[wh][0] = upper < '1.0' or lower > '0.0'
            size[wh][1] += 20 * size[wh][0] # += 1 for accuracy but slower
        # Call the is_scroll function when textwidget scrolls
        textwidget.config(xscrollcommand=lambda *args: is_scroll('w', *args),
                          yscrollcommand=lambda *args: is_scroll('h', *args))

        # Add a tk.Button to the Frame (self) and its configuration
        tk.Button(self, text="OK", command=self.quit).grid(row=1, column=0,
                                                           sticky="we")

        # For reasons of magic, hide root window NOW before updating
        root.withdraw()

        # Initially, make root window a minimum of 50 x 50 just for kicks
        root.geometry('50x50')
        size = {'w': [False, 50], 'h': [False, 50]}
        # Update to trigger the is_scroll function
        root.update()
        while size['w'][0] or size['h'][0]:
            # If here, we need to update the size of the root window
            root.geometry('{}x{}'.format(size['w'][1], size['h'][1]))
            root.update()

        # Center root window on mouse pointer
        x, y = root.winfo_pointerxy()
        root.geometry('+{}+{}'.format(x-size['w'][1]//2, y-size['h'][1]//2))

        # Now reveal the root window in all its glory
        root.deiconify()

        # Print textwidget dimensions to the console
        print(textwidget.winfo_width(), textwidget.winfo_height())

def main():
    """Show main window."""
    MyFrame().mainloop()

if __name__ == '__main__':
    main()
