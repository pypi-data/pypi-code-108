import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.ttk as ttk

from IPy import IP


class Widgets():

    def __init__(self, parent) -> None:
        self.parent = parent

    def widgetmaking(self, port: int):
        """
                Defining all Widgets

                Seperate Functions:
                self.usernamewidget() -> usernamewidget-Labels etc
                self.makeIPFrame() -> IP-Widgets etc
                self.makeMessageWidgets() -> explains itself
                self.configuregridweight() -> configures the weigths of the colums and rows
        """
        # Name-Label & Entry
        self.usernamewidget()

        # IP-Eingabe
        self.makeIPFrame(port)

        self.parent.ausgabe = scrolledtext.ScrolledText()
        self.parent.ausgabe.grid(row=3,
                                 column=0,
                                 columnspan=4,
                                 sticky="ew")
        self.parent.ausgabe.tag_config("right", justify="right")

        self.makeMessageWidgets()

        self.parent.send_Button = ttk.Button(self.parent)
        self.parent.send_Button["text"] = "Send"
        self.parent.send_Button["command"] = self.parent.sendmessage
        self.parent.send_Button.grid(row=4,
                                     column=3,
                                     sticky="w")

        # configuring
        self.parent.settings.configuregridweight()
        self.parent.ausgabe.configure(state='disabled')
        self.parent.name_Entry.focus()
        return

    def makeMessageWidgets(self):
        self.parent.msgcmd = self.parent.register(self.validmessage)
        self.parent.lengthvar = tk.StringVar()
        self.parent.lengthvar.set("Remaining Characters: 1000")

        self.parent.message_label = ttk.Label(self.parent)
        self.parent.message_label["text"] = "Nachricht (max. 1000 characters):"

        self.parent.msg_Entry = ttk.Entry(self.parent)
        self.parent.msg_Entry["validate"] = "key"
        self.parent.msg_Entry["validatecommand"] = (self.parent.msgcmd, "%P")

        self.parent.length_Label = ttk.Label(self.parent)
        self.parent.length_Label["textvariable"] = self.parent.lengthvar

        self.parent.message_label.grid(row=4,
                                       column=0,
                                       sticky="w")
        self.parent.msg_Entry.grid(row=4,
                                   column=1,
                                   sticky="w")
        self.parent.length_Label.grid(row=4,
                                      column=2,
                                      sticky="w")

        self.parent.msg_Entry.bind("<Return>",
                                   self.parent.sendmessage)
        return

    def usernamewidget(self):
        """
        Defines the Username-Widgets (and Port)
        - UsernameFrame
        - name_Entry
        """
        self.parent.usernamecmd = self.parent.register(self.validusername)

        self.parent.UsernameFrame = ttk.LabelFrame(self.parent)
        self.parent.UsernameFrame["text"] = "Username: (max. 9 characters)"
        self.parent.UsernameFrame["relief"] = tk.SUNKEN

        self.parent.name_Entry = ttk.Entry(self.parent.UsernameFrame)
        self.parent.name_Entry["validate"] = "key"
        self.parent.name_Entry["validatecommand"] = (
            self.parent.usernamecmd, "%P")

        self.parent.sound_variable = tk.IntVar(self.parent)
        self.parent.sound_variable.set(1)
        self.parent.sound_Checkbox = ttk.Checkbutton(self.parent.UsernameFrame)
        self.parent.sound_Checkbox["text"] = "Message Sound"
        self.parent.sound_Checkbox["variable"] = self.parent.sound_variable

        self.parent.topmost_Button = ttk.Button(
            self.parent.UsernameFrame, text="AlwaysOnTop", command=self.parent.settings.makeTopMost, style='topmost.TButton')

        self.parent.UsernameFrame.grid(row=0,
                                       column=0,
                                       columnspan=4,
                                       sticky="nsew")
        self.parent.name_Entry.pack(side="left")
        self.parent.sound_Checkbox.pack(side="left")
        self.parent.topmost_Button.pack(side="right")
        return

    def makeIPFrame(self, port: int):
        self.parent.vcmd = self.parent.register(self.checkIPEntry)

        self.parent.BigFrame = ttk.LabelFrame(self.parent)
        self.parent.BigFrame["text"] = "Empfänger (IP):"
        self.parent.IPframe = ttk.LabelFrame(self.parent.BigFrame)
        self.parent.IPframe["text"] = "Enter IP Here"
        self.parent.IPframe["relief"] = tk.SUNKEN

        self.parent.ip_Entry_1 = ttk.Entry(self.parent.IPframe)
        self.parent.ip_dot1 = ttk.Label(self.parent.IPframe, text=".")
        self.parent.ip_Entry_2 = ttk.Entry(self.parent.IPframe)
        self.parent.ip_dot2 = ttk.Label(self.parent.IPframe, text=".")
        self.parent.ip_Entry_3 = ttk.Entry(self.parent.IPframe)
        self.parent.ip_dot3 = ttk.Label(self.parent.IPframe, text=".")
        self.parent.ip_Entry_4 = ttk.Entry(self.parent.IPframe)

        self.parent.ip_Entry_1["width"] = self.parent.ip_Entry_2[
            "width"] = self.parent.ip_Entry_3["width"] = self.parent.ip_Entry_4["width"] = 5
        self.parent.ip_Entry_1["validate"] = self.parent.ip_Entry_2[
            "validate"] = self.parent.ip_Entry_3["validate"] = self.parent.ip_Entry_4["validate"] = "key"
        self.parent.ip_Entry_1["validatecommand"] = self.parent.ip_Entry_2["validatecommand"] = self.parent.ip_Entry_3[
            "validatecommand"] = self.parent.ip_Entry_4["validatecommand"] = (self.parent.vcmd, "%P")

        self.parent.invalidIP_Label = ttk.Label(self.parent.IPframe)
        self.parent.invalidIP_Label["text"] = "Invalid IP !"
        self.parent.invalidIP_Label["foreground"] = "red"

        self.parent.port_Label = ttk.Label(self.parent.BigFrame)
        self.parent.port_Label["text"] = f"Port: {port}"

        self.parent.BigFrame.grid(row=1,
                                  column=0,
                                  columnspan=4,
                                  sticky="nsew")
        self.parent.IPframe.pack(side="left")

        self.parent.ip_Entry_1.pack(side="left")
        self.parent.ip_dot1.pack(side="left")
        self.parent.ip_Entry_2.pack(side="left")
        self.parent.ip_dot2.pack(side="left")
        self.parent.ip_Entry_3.pack(side="left")
        self.parent.ip_dot3.pack(side="left")
        self.parent.ip_Entry_4.pack(side="left")

        self.parent.port_Label.pack(side="right")

        self.parent.ip_Entry_1.bind("<FocusIn>", self.deleteinvIPLabel)
        self.parent.ip_Entry_2.bind("<FocusIn>", self.deleteinvIPLabel)
        self.parent.ip_Entry_3.bind("<FocusIn>", self.deleteinvIPLabel)
        self.parent.ip_Entry_4.bind("<FocusIn>", self.deleteinvIPLabel)
        return

    def checkIPEntry(self, ippart) -> bool:
        if ippart:
            if ippart.isdigit() and int(ippart) <= 255 and int(ippart) >= 0:
                return True
            self.parent.bell()
            return False
        else:
            return True

    def deleteinvIPLabel(self, event=None):
        self.parent.invalidIP_Label.pack_forget()
        return

    def validmessage(self, message) -> bool:
        self.parent.lengthvar.set(
            "Remaining Characters: " + str(1000 - len(message)))
        return self.check_length(message, 1000)

    def validusername(self, username) -> bool:
        return self.check_length(username, 9)

    def check_length(self, arg0, arg1) -> bool:
        if len(arg0) <= arg1:
            return True
        self.parent.bell()
        return False

    def validIP(self) -> bool:
        if self.parent.user_IP == "...":
            return True
        try:
            IP(self.parent.user_IP)
        except Exception:
            return False
        else:
            return True


class Settings():

    def __init__(self, parent):
        self.parent = parent

    def makeTopMost(self) -> None:
        self.parent.buttonstyle = ttk.Style()
        if self.parent.wm_attributes("-topmost") == 1:
            self.parent.wm_attributes("-topmost", 0)
            self.parent.buttonstyle.configure(
                'topmost.TButton', background='SystemButtonFace')
        else:
            self.parent.wm_attributes("-topmost", 1)
            self.parent.buttonstyle.configure(
                'topmost.TButton', background='palegreen')
        return

    def windowsettings(self) -> None:
        self.parent.title("Python Messenger")
        return

    def configuregridweight(self) -> None:
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_rowconfigure(2, weight=1)
        self.parent.grid_rowconfigure(3, weight=1)
        self.parent.grid_rowconfigure(4, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        return


__all__ = ["Widgets", "Settings"]

if __name__ == "__main__":
    print("test")
    print("test")
