# -*- coding: utf-8 -*-

from .Dumper import SSHProfileDumper
from . import SSH as ssh 
from .Domain import AdditionalOption, SSHConnection
from .Domain import SSHProfile
from .Domain import PortForwarding
from .Errors import SSHConnectionNotFoundError

import socket
from time import sleep

class Runner:
    def __init__(self):
        self.dumper = SSHProfileDumper()
        self.ssh_profile = self.dumper.load()

    def list_and_prompt(self):
        self.list()
        option = get_string_input("\nInsert name or number: ", "None")

        if option != "None" and option != None and option != "":
            return option
        else:
            raise Exception("No connection name or number was given.")

    def connect_prompt(self):
        connection = self.list_and_prompt()
        self.connect(connection)
    
    def connect(self, connection_name):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            ssh_connection = None

            if connection_name.isdigit():
                ssh_connection = self.ssh_profile.profiles[int(connection_name) - 1]
            else:
                for connection in self.ssh_profile.profiles:
                    if connection.name == connection_name:
                        ssh_connection = connection 
                        break

            if ssh_connection != None: 
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server = ssh_connection.server_url
                port = ssh_connection.ssh_port

                #check if server is up
                if sock.connect_ex((server, port)) == 0:
                    ssh.run(ssh_connection)
                else:
                    print("Connection to server {} was not successful, maybe it is not reachable?".format(ssh_connection.name))

            else:
                raise SSHConnectionNotFoundError(connection_name + " does not exist.")
    
    def show_prompt(self):
        connection = self.list_and_prompt()
        self.show_connection(connection)

    def show_connection(self, connection_name):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            ssh_connection = None

            if connection_name.isdigit():
                ssh_connection = self.ssh_profile.profiles[int(connection_name) - 1]
            else:
                for connection in self.ssh_profile.profiles:
                    if connection.name == connection_name:
                        ssh_connection = connection 
                        break

            if ssh_connection != None: 
                print("--- Index: " + str(self.ssh_profile.profiles.index(ssh_connection) + 1))
                print(ssh_connection)
            else:
                raise SSHConnectionNotFoundError(connection_name + " does not exist.")
       
    def list(self):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            print(self.ssh_profile, end="")

    def add(self, name, fwd_list, key_path, user, 
        server_url, ssh_port, addl_options=[]):

        new_ssh = SSHConnection(name, user, server_url, ssh_port, key_path)

        for fwd in fwd_list:
            new_ssh.forwardings.append(fwd)

        for addl_option in addl_options:
            new_ssh.additional_options.append(addl_option)
        
        self.ssh_profile.profiles.append(new_ssh)
        self.dumper.save(self.ssh_profile)

    def add_prompt(self, name = None):
        if self.ssh_profile == None:
            self.ssh_profile = SSHProfile()

        if name == None:
            name = get_string_input("Insert connection name:", "new_connection")

        user = input("Insert username: ")
        if user == None or user == "":
            print("Cannot proceed without a username.")
            return

        server_url = input("Insert Server URL: ")
        if server_url == None or server_url == "":
            print("Cannot proceed without Server URL.")
            return
        
        ssh_port = 22
        option = get_string_input("Will you change the default SSH port? [y/n]", "n")
        if str.lower(option) == "y":
            ssh_port = get_int_input("Insert SSH port: ", 22)

        ssh_key = None
        option = get_string_input("Will you use ssh private key? [y/n]", "n")
        if str.lower(option) == "y":
            ssh_key = input("Insert SSH key path: ")
        
        local_port, dest_ip_dns, dest_port = None, None, None
        option = get_string_input("Will you use port forwarding? [y/n]", "n")
        forwardings = []

        while(str.lower(option) == "y"):
            local_port = input("Insert local port: ")
            dest_ip_dns = input("Insert destination URL: ")
            dest_port = input("Insert destination port: ") 

            fwd = PortForwarding(local_port, dest_ip_dns,
                    dest_port)
            forwardings.append(fwd)

            option = get_string_input("Will you add another port forwarding? [y/n]", "n")

        additional_option_name, additional_option_value = None, None
        option = get_string_input("Will you use additional options? [y/n]", "n")
        additional_options = []

        while(str.lower(option) == "y"):
            additional_option_name = input("Insert option name: ")
            additional_option_value = input("Insert option value: ")

            addl_option = AdditionalOption(additional_option_name, additional_option_value)
            additional_options.append(addl_option)

            option = get_string_input("Will you add another additional option? [y/n]", "n")

        self.add(name, forwardings, ssh_key, user, 
            server_url, ssh_port, additional_options)

    def add_cmd(self, name, ssh_cmd):
        connection = SSHConnection.from_ssh_cmd(name, ssh_cmd)
        self.ssh_profile.profiles.append(connection)
        self.dumper.save(self.ssh_profile)

    def edit_prompt(self, name = None):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            if name == None:
                name = self.list_and_prompt() 

            if name != "None":
                old_ssh = name
                new_ssh = None

                if old_ssh.isdigit():
                    old_ssh = self.ssh_profile.profiles[int(old_ssh) - 1]
                else:
                    for connection in self.ssh_profile.profiles:
                        if connection.name == old_ssh:
                            old_ssh = connection

                            break


                if old_ssh != None:

                    new_ssh = SSHConnection(old_ssh.name, old_ssh.user, 
                            old_ssh.server_url)
                    new_ssh.ssh_port = old_ssh.ssh_port
                    new_ssh.key_path = old_ssh.key_path
                    new_ssh.forwardings = old_ssh.forwardings
                    new_ssh.additional_options = old_ssh.additional_options

                    new_name = get_string_input("Insert a new connection name:", old_ssh.name)
                    if new_name != None and new_name != "":
                        new_ssh.name = new_name
                    else:
                        new_ssh.name = old_ssh.name

                    user = get_string_input("Insert new username: ", old_ssh.user)
                    if user != None and user != "":
                        new_ssh.user = user
                    else:
                        new_ssh.user = old_ssh.user

                    server_url = get_string_input("Insert Server URL: ", old_ssh.server_url)
                    if server_url != None and server_url != "":
                        new_ssh.server_url = server_url
                    else:
                        new_ssh.server_url = old_ssh.server_url
                   
                    option = get_string_input("Will you change the SSH port? [y/n]", "n")
                    if str.lower(option) == "y":
                        ssh_port = get_int_input("Insert SSH port: ", old_ssh.ssh_port)
                        if (ssh_port != None and ssh_port != ""):
                            new_ssh.ssh_port = ssh_port
                        else:
                            new_ssh.ssh_port = old_ssh.ssh_port

                    option = get_string_input("Will you change the ssh private key? [y/n]", "n")
                    if str.lower(option) == "y":
                        ssh_key = get_string_input("Insert a new SSH key path: ", old_ssh.key_path)
                        if (ssh_key != None and ssh_key != ""):
                            new_ssh.key_path = ssh_key
                        else:
                            new_ssh.key_path = old_ssh.key_path
                    
                    local_port, dest_ip_dns, dest_port = None, None, None
                    option = get_string_input("Will you edit port forwardings? [y/n]", "n")
                    
                    new_ssh.forwardings = old_ssh.forwardings

                    while(str.lower(option) == "y"):
                        print("Available forwardings:")
                        print()

                        count = 0
                        for fwd in new_ssh.forwardings:
                            print(str(count + 1) + " - " +
                                   str(fwd.fwd_local_port) + ":" +
                                   str(fwd.fwd_dest_ip_dns) + ":" +
                                   str(fwd.fwd_dest_port))
                            count += 1

                        option = get_int_input("Which one will you edit?", -1)

                        if option > -1:
                            local_port = input("Insert a new local port: ")
                            dest_ip_dns = input("Insert a new destination URL: ")
                            dest_port = input("Insert a new destination port: ") 

                            fwd = PortForwarding(local_port, dest_ip_dns,
                                    dest_port)
                            new_ssh.forwardings[option - 1] = fwd

                        option = get_string_input("Keep editing port forwardings? [y/n]", "n")

                    additional_option_name, additional_option_value = None, None
                    option = get_string_input("Will you edit additional options? [y/n]", "n")

                    while(str.lower(option) == "y"):
                        print("Available additional options:")
                        print()

                        count = 0
                        for addl_option in new_ssh.additional_options:
                            print(str(count + 1) + " - " +
                                   str(addl_option.option_name) + "=" +
                                   str(addl_option.option_value))
                            count += 1

                        option = get_int_input("Which one will you edit?", -1)

                        if option > -1:
                            additional_option_name = input("Insert option name: ")
                            additional_option_value = input("Insert option value: ")

                            addl_option = AdditionalOption(additional_option_name, additional_option_value)
                            new_ssh.additional_options[option - 1] = addl_option

                        option = get_string_input("Keep editing additional options? [y/n]", "n")

                    self.edit(old_ssh.name, new_ssh.name, new_ssh.forwardings, 
                            new_ssh.key_path, new_ssh.user, 
                        new_ssh.server_url, new_ssh.ssh_port, new_ssh.additional_options)
                   
                else:
                    print("Connection not found.")

    def edit(self, connection_name, new_name, fwd_list, ssh_key,
        user, server_url, ssh_port, addl_options=[]):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            old_ssh = 0

            for connection in self.ssh_profile.profiles:
                if connection.name == connection_name:
                    break
                old_ssh += 1

            new_ssh = SSHConnection(new_name, user, server_url, 
                ssh_port, ssh_key)

            for fwd in fwd_list:
                new_ssh.forwardings.append(fwd)

            for addl_option in addl_options:
                new_ssh.additional_options.append(addl_option)
            
            self.ssh_profile.profiles[old_ssh] = new_ssh
            self.dumper.save(self.ssh_profile)

    def remove(self, connection_name):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            for connection in self.ssh_profile.profiles:
                if connection.name == connection_name:
                    self.ssh_profile.profiles.remove(connection)
                    self.dumper.save(self.ssh_profile)
                    break

    def reorder(self):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            print("Arranging SSH Profiles in alphabetical order... ", end="")
            names_list = []

            for profile in self.ssh_profile.profiles:
                names_list.append(profile.name)

            names_list.sort()

            new_profile_list = []

            for name in names_list:
                for profile in self.ssh_profile.profiles:
                    if profile.name == name:
                        new_profile_list.append(profile)
                        self.ssh_profile.profiles.remove(profile)

            self.ssh_profile.profiles = new_profile_list
            self.dumper.save(self.ssh_profile)
            print("Done.")

    def copy(self, fileA, fileB, r=None):
        ssh_connection = None
        connection_name = None
        remote_file = None
        local_file = None
        operation = None
        if ':' in "\t".join(fileA):
            remote_file = fileA
            local_file = fileB
            operation = ssh.SCP_OPERATION_DOWNLOAD
        else:
            remote_file = fileB
            local_file = fileA
            operation = ssh.SCP_OPERATION_UPLOAD

        connection_name = remote_file[0].split(':')[0]
        remote_file = remote_file[0].split(':')[1].replace(':','')

        if connection_name.isdigit():
            ssh_connection = self.ssh_profile.profiles[int(connection_name) - 1]
        else:
            for connection in self.ssh_profile.profiles:
                if connection.name == connection_name:
                    ssh_connection = connection 
                    break

        ssh_connection.set_scp_operation(remote_file, local_file, operation, r=r)
        ssh.scp(ssh_connection)

    def wait_for(self, connection_name):
        if self.ssh_profile == None:
            print("There are no SSH Connections set.")
        else:
            ssh_connection = None

            if connection_name.isdigit():
                ssh_connection = self.ssh_profile.profiles[int(connection_name) - 1]
            else:
                for connection in self.ssh_profile.profiles:
                    if connection.name == connection_name:
                        ssh_connection = connection 
                        break

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server = ssh_connection.server_url
            port = ssh_connection.ssh_port

            if ssh_connection != None: 
                while not sock.connect_ex((server, port)) == 0:
                    print("Connection to server {} was not successful, trying again in 2 seconds...".format(ssh_connection.name))
                    sleep(2)
                ssh.run(ssh_connection)
            else:
                raise SSHConnectionNotFoundError(connection_name + " does not exist.")


#aux functions
def get_int_input(message, default_value):
    try:
        return int(input(message + " [Default " + str(default_value) + "] "))
    except ValueError:
        return default_value

def get_string_input(message, default_value):
    try:
        string = str(input(message + " [Default " + str(default_value) + "] "))
        return string if string != "" else default_value
    except ValueError:
        return default_value
