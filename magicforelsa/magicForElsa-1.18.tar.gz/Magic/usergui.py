from tkinter import Tk, Entry

from Magic import file_database
from Magic.tkinterlib import TLabel, TButton, tkinter_initialise, TLabelFrame
from talk1.talk1 import talk


def user_page()->None:
    """This function is used to implement the GUI of the add user page"""
    userpage = Tk()
    tkinter_initialise(userpage, 600, 340)
    s = TLabelFrame(userpage, text="Add New User")
    s.grid(row=0, column=0)
    TLabel(s, text="Enter the username:").grid(row=0, column=0)
    TLabel(s, text="Enter the password:").grid(row=1, column=0)
    eu, ep = Entry(s), Entry(s)
    eu.grid(row=0, column=1)
    ep.grid(row=1, column=1)

    def add(event="")->None:
        """[Adds the user]"""
        new_user, new_password = eu.get(), ep.get()
        talk(f"Successfully added {new_user}" if (file_database.write_to_file(new_user, new_password)) == 1 else "User already exists. Try again")
        userpage.destroy()

    TButton(s, text="Add User", command=add).grid(row=3, column=1)
    TButton(s, text="X", command=userpage.destroy).grid(row=3, column=0)
    userpage.bind("<Return>", add)
    userpage.mainloop()


def deleteuser()->None:
    """This function is used to implement the GUI of the delete user page"""
    deleteuserpage = Tk()
    talk("Please enter the username and password to delete")
    tkinter_initialise(deleteuserpage, 600, 340)
    s = TLabelFrame(deleteuserpage, text="Delete User")
    s.grid(row=0, column=0)
    TLabel(s, text="Enter the username to delete:").grid(row=0, column=0)
    TLabel(s, text="Enter the password:").grid(row=1, column=0)
    TLabel(s, text="Retype the password:").grid(row=2, column=0)
    eu, ep, epr = Entry(s), Entry(s), Entry(s)
    eu.grid(row=0, column=1)
    ep.grid(row=1, column=1)
    epr.grid(row=2, column=1)

    def deleteuserfunc(event="")->None:
        """[Delete  the user backend]"""
        name_delete = eu.get()
        password = ep.get()
        retypepassword = epr.get()
        if retypepassword == password:
            try:
                import json
                import os
                from pathlib import Path
                userdata = json.load(userfile := open(Path(userpth := (os.getcwd() + "/resources/ users.elsa"))))
                userfile.close()
                try:
                    if userdata[name_delete] == password:
                        del userdata[name_delete]
                        deleteuserpage.destroy()
                        userfile = open(Path(userpth), "w")
                        userdata["admin"] = "1234"  # add admin back in case it is deleted
                        print("Deleted user", name_delete)
                        json.dump(userdata, userfile, indent=4)
                        userfile.close()
                        talk("User successfully deleted")
                    else:
                        print("Sorry. your username and password do not match")
                        talk("Sorry. your username and password do not match")
                except: talk("Sorry,such a user do not exist. Please try again")
            except: talk("Sorry, but the passwords do not match")
        else:
            print("Passwords in both the field do not match")
            talk("Passwords in both the field do not match. Please try again")

    TButton(s, text="Delete User", command=deleteuserfunc).grid(row=3, column=1)
    TButton(s, text="X", command=deleteuserpage.destroy).grid(row=3, column=0)
    deleteuserpage.bind("<Return>", deleteuserfunc)
    deleteuserpage.mainloop()
