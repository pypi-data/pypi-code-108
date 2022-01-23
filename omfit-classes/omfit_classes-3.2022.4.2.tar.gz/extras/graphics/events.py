import tkinter as tk

root = tk.Tk()


def report_event_details(event):
    print(event.state, event.keysym, event.keycode)


text = tk.Text(root)
text.grid()
text.bind("<Key>", report_event_details, True)

button = tk.Button(root, text="Dummy")
button.grid()

root.mainloop()
