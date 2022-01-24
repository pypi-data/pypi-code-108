import json
import socket as st
from threading import Thread
import tkinter as tk
from datetime import datetime
from dataclasses import dataclass


class MessengerSocket(st.socket):
    def __init__(self, family: st.AddressFamily = st.AF_INET, type: st.SocketKind = st.SOCK_DGRAM) -> None:
        super(MessengerSocket, self).__init__(family, type)


def startlistening(self) -> None:
    receivethread = Thread(target=self.listenformsg, daemon=True)
    receivethread.start()


def listenformsg(self) -> None:
    while True:
        jsondata, addr = self.serversocket.recvfrom(1024)
        if self.sound_variable.get():
            self.play()
        self.incmessage = Message()
        self.incmessage.updt(jsondata)
        self.ausgabe.configure(state='normal')
        current_time = datetime.now().strftime("%H:%M")
        if self.incmessage.name != "":
            if addr[0] == "127.0.0.1":
                self.ausgabe.insert(
                    tk.END, f"[{current_time}] {self.incmessage.name} (You): '{self.incmessage.msg}' \n")
            else:
                self.ausgabe.insert(
                    tk.END, f"[{current_time}] {self.incmessage.name} : '{self.incmessage.msg}' \n")
        elif addr[0] == "127.0.0.1":
            self.ausgabe.insert(
                tk.END, f"[{current_time}] {addr[0]} (You): '{self.incmessage.msg}' \n")
        else:
            self.ausgabe.insert(
                tk.END, f"[{current_time}] {addr[0]} : '{self.incmessage.msg}' \n")
        self.ausgabe.configure(state='disabled')
        self.ausgabe.see("end")


def sendmessage(self, event=None) -> None:
    """Funktion zum Senden einer Nachricht"""

    if self.msg_Entry.get() == "":
        return
    self.empfaenger = "localhost"
    if not self.widg.validIP():
        self.bell()
        self.invalidIP_Label.pack()
    else:
        self.send()
    return


def send(self) -> None:
    if self.user_IP != "...":
        self.empfaenger = self.user_IP
    self.message = self.Message(name=self.name_Entry.get(),
                                msg=self.msg_Entry.get())
    # senden der Nachricht an Ziel-Adresse über Socket
    self.serversocket.sendto(self.message.encoded(),
                             (self.empfaenger, self.port))
    # löschen des Inhalts des Eingabe-Widgets
    self.ausgabe.configure(state='normal')
    if self.message.name == "":
        self.ausgabe.insert(
            tk.END, f"You: '{self.message.msg}'\n", "right")
    else:
        self.ausgabe.insert(
            tk.END, f"{self.message.name} (You): '{self.message.msg}'\n", "right")
    self.ausgabe.configure(state='disabled')
    self.ausgabe.see("end")
    self.msg_Entry.delete(0, tk.END)
    return


@dataclass
class Message:
    name: str = ""
    msg: str = ""

    def __jsondumps(self) -> str:
        return json.dumps(self.__dict__)

    def __jsonloads(self, jsonmsg: bytes) -> dict:
        return json.loads(self.__decoded(jsonmsg))

    def __decoded(self, jsonmsg: bytes) -> str:
        return jsonmsg.decode("utf-8")

    def encoded(self) -> bytes:
        return self.__jsondumps().encode("utf-8")

    def updt(self, jsonmsg: bytes) -> None:
        self.__dict__.update(self.__jsonloads(jsonmsg))
        return


if __name__ == '__main__':
	print("networking")
