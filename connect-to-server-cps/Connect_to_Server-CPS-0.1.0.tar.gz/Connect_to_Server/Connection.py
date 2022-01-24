import paramiko
import sys
import os
import re


class Connection:
    """
        This script would connect to a server, find the LaTeX files, integrate the LaTeX's input and include functions,
        and save the file at a new directory defined by user. No matter how many files the directory in the server
        contains. The code will go through each folder and find the LaTeX files and write them at the new directory
        maintaining the directory structure in the server.

        :param host: The host of the server.
        :type host: str
        :param username: The username of the user.
        :type username: str
        :param password: The password of the user.
        :type password: str
        :param directory: The directory that you want to find the LaTeX files.
        :type directory: str
        :param Save_at: The new directory that you want to save the integrated LaTeX files.
        :type Save_at: str
    """

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def expanded_input(text):  # This function integrates the LaTeX files referred by \input{directory of the LaTeX file}
        new_subdir = filepath
        for input in re.findall(r"\n\\input{(?P<sub_path>.*)}", text):
            new_path = new_subdir
            for sub_folder in input.split("/"):
                new_path = new_path + "/" + sub_folder
            if new_path.endswith(".tex") or new_path.endswith(".TEX"):
                new_path = new_path.replace(".tex", "")
                new_path = new_path.replace(".TEX", "")
                new_path = new_path.replace(" ", "\ ")  # Some files in the directory have spaces in their name. By adding this line, we can read those files.
            tex_folder = re.sub(new_path.split("/")[-1], '', new_path)
            ssh_stdin5, ssh_stdout5, ssh_stderr5 = ssh.exec_command("ls " + tex_folder)
            for line5 in ssh_stdout5:
                if line5.strip().endswith(".tex") or line5.strip().endswith(".TEX"):
                    if line5.strip().split(".")[0].lower() == new_path.split("/")[-1].lower():
                        new_path = tex_folder + line5.strip()
            try:
                ssh_stdin4, ssh_stdout4, ssh_stderr4 = ssh.exec_command("less " + new_path)
            except OSError:
                continue
            try:
                # sub_text = ssh_stdout4.read().decode(encoding='utf-8') #I don't know why this line is not working. So, I add the following lines which do the same work done by this line. However, it takes more time.
                sub_text = ""
                for line4 in ssh_stdout4:
                    sub_text = sub_text + "\n" + line4.strip()
            except UnicodeDecodeError:
                sub_text = ssh_stdout4.read().decode(encoding='windows-1252')
            if re.findall(r"\n\\input{(?P<sub_path>.*)}", sub_text) != []:
                print("yes")
                sub_text = expanded_input(sub_text)
            text = text.replace("\n" + "\\" + "input{" + input + "}",
                                "\n" + "%" + "\\" + "input{" + input + "}" + "\n" + sub_text)
        print("55")
        return text

    def expanded_include(text):  # This function integrates the LaTeX files referred by \input{directory of the LaTeX file}
        new_subdir = filepath
        for inc in re.findall(r"\n\\include{(?P<sub_path>.*)}", text):
            new_path = new_subdir
            for sub_folder in inc.split("/"):
                new_path = new_path + "/" + sub_folder
            if new_path.endswith(".tex") or new_path.endswith(".TEX"):
                new_path = new_path.replace(".tex", "")
                new_path = new_path.replace(".TEX", "")
                new_path = new_path.replace(" ",
                                            "\ ")  # Some files in the directory have spaces in their name. By adding this line, we can read those files.
            tex_folder = re.sub(new_path.split("/")[-1], '', new_path)
            ssh_stdin5, ssh_stdout5, ssh_stderr5 = ssh.exec_command("ls " + tex_folder)
            for line5 in ssh_stdout5:
                if line5.strip().endswith(".tex") or line5.strip().endswith(".TEX"):
                    if line5.strip().split(".")[0].lower() == new_path.split("/")[-1].lower():
                        new_path = tex_folder + line5.strip()
            try:
                ssh_stdin4, ssh_stdout4, ssh_stderr4 = ssh.exec_command("less " + new_path)
            except OSError:
                continue
            try:
                # sub_text = ssh_stdout4.read().decode(encoding='utf-8') #I don't know why this line is not working. So, I add the following lines which do the same work done by this line. However, it takes more time.
                sub_text = ""
                for line4 in ssh_stdout4:
                    sub_text = sub_text + "\n" + line4.strip()
            except UnicodeDecodeError:
                sub_text = ssh_stdout4.read().decode(encoding='windows-1252')
            text = text.replace("\n" + "\\" + "include{" + inc + "}",
                                "\n" + "%" + "\\" + "include{" + inc + "}" + "\n" + sub_text)
        return text

    def Connect(self):
        global ssh
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(f'{self.host}', port=22, username=f'{self.username}', password=f'{self.password}')
        return ssh

    def Find_and_Integrate(self, directory, Save_at):
        global filepath
        root_path = Save_at
        path = directory
        ssh = Connection.Connect(self)
        ssh_stdin1, ssh_stdout1, ssh_stderr1 = ssh.exec_command("ls -R " + path)  # This line will list the files in the server. It also gives the directory of each file.
        for line1 in ssh_stdout1:
            if line1.strip().endswith(":"):  # Line1 includes the directoy of files in the path in the server.
                filepath = line1.strip().split(":")[0]
                ssh_stdin2, ssh_stdout2, ssh_stderr2 = ssh.exec_command("ls " + filepath)
                for line2 in ssh_stdout2:
                    if line2.strip().endswith(".tex") or line2.strip().endswith(".TEX"):  # Line2 returns the LaTeX files in the Line1.
                        filename = line2.strip()
                        filename = filename.replace(" ", "\ ")  # Some files in the directory have spaces in their name. By adding this line, we can read those files.
                        ssh_stdin3, ssh_stdout3, ssh_stderr3 = ssh.exec_command("less " + filepath + "/" + filename)
                        try:
                            #    text = ssh_stdout3_utf_8.read().decode(encoding='utf-8')   #I don't know why this line is not working. So, I add the following lines which do the same work done by this line. However, it takes more time.
                            text = ""
                            for line3 in ssh_stdout3:
                                text = text + "\n" + line3.strip()
                        except:
                            text = ssh_stdout3.read().decode(encoding='windows-1252')  # There are a few files that must be encoded by "windows-1252"
                        if re.findall(r"\n\\input{(?P<sub_path>.*)}", text) != []:
                            text = Connection.expanded_input(text)
                            print("line 120")
                        if re.findall(r"\n\\include{(?P<sub_path>.*)}", text) != []:
                            text = Connection.expanded_include(text)
                        new_directory = root_path + filepath  # Make a directory to store the files
                        try:
                            os.makedirs(new_directory)
                        except:
                            print("--------------------------")
                        newfilename = "New_" + filename.replace("\ ", " ")
                        print(new_directory + "/" + newfilename)
                        f = open(new_directory + "/" + newfilename.lower(), "w+", encoding="utf-8")
                        f.write(text)