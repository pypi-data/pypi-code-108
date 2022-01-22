#!/usr/bin/env python3
from netdevice import cisco, junos, linux
#linux.default["log_level"] = linux.LOG_NOTICE

if __name__ == '__main__':
    dut = junos.JunosDevice(
            "ssh://root:your_password@bj4100a.englab.juniper.net")
    client = linux.LinuxDevice(username = "root",
            password = "your_password",
            hostname = "ent-vm01.englab.juniper.net",
            interfaces = [ { 'name': 'eth1',
                'inet': '41.0.0.2/24',
                'inet6': '2001::2/64'} ])
    server = linux.LinuxDevice(username = "root",
            password = "your_password",
            hostname = "ent-vm02.englab.juniper.net",
            interfaces = [ { 'name': 'eth1',
                'inet': '42.0.0.2/24',
                'inet6': '2002::2/64'} ])

    #client.cmd("ip route add 42.0.0.0/24 via 41.0.0.1 dev eth1")
    #server.cmd("ip route add 41.0.0.0/24 via 42.0.0.1 dev eth1")
    dut.cli("clear security flow session application ftp")

    # connect to the server and list the files.
    client.cmd('ftp %s' %(server["interfaces"][0]["inet"].split('/')[0]),
            expect = "Name")
    client.cmd(server["username"], expect = "Password")
    client.cmd(server["password"], expect = "ftp")
    (status, output) = client.cmd('ls', expect = "ftp> ", format = "both")
    if status and "226" in output:
        print("ftp output is shown.")
    else:
        print("ftp failed to connect the server.")

    # check the session and tear down the connection.
    sessions = dut.cli('show security flow session application ftp',
            parse = "flow-session")
    client.cmd('bye')

    print(sessions[0]["flow-information"][0]['pkt-cnt'])
    print(type(sessions[0]["flow-information"][0]['pkt-cnt']))
    if (sessions and \
        int(sessions[0]["flow-information"][0]['pkt-cnt']) > 0 and \
        int(sessions[0]["flow-information"][1]['pkt-cnt']) > 0):
        print("Session found, pass!")
    else:
        print("Failed to find the session")
