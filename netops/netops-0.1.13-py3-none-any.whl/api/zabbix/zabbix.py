import sys
import logging
from pyzabbix import ZabbixAPI
from time import sleep


def init_zapi(zabbix_url, zabbix_user, zabbix_pass):
    """
	TODO: write docstrings
	"""

    zapi = ZabbixAPI(zabbix_url)
    # API Token authentication is just able with Zabbix >= 5.4
    # zapi.login(api_token='xxxxx')
    zapi.login(zabbix_user, zabbix_pass)
    print("Connected to Zabbix API Version %s\n" % zapi.api_version())

    """
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    log = logging.getLogger('pyzabbix')
    log.addHandler(stream)
    log.setLevel(logging.DEBUG)
    """
    
    return zapi


def get_hostid(zapi, host_name):
    """
	TODO: write docstrings
	"""

    print(f"Getting host ID of host {host_name} from Zabbix API...")
    hosts_filtered = zapi.host.get(output="extend", filter={"host": host_name})
    #print(f"Hosts got from Zabbix API: {hosts_filtered}")
    if hosts_filtered == []:
        print(f"ERROR! Host '{host_name}' could not be find on Zabbix.")
        print(f"ERROR! Please check the host name on {zapi.url}\n")
        exit(1)

    for h in hosts_filtered:
        if h['host'] == host_name:
            h_updated = h
    #print("Host match: ", h_updated)
    
    return h_updated['hostid']


def get_hostname(zapi, zhostid):
    """
	TODO: write docstrings
	"""

    print(f"Getting host ID {zhostid} from Zabbix API...\n")
    hosts_filtered = zapi.host.get(output="extend", filter={"hostid": zhostid})
    #print(f"Hosts got from Zabbix API: {hosts_filtered}")
    if hosts_filtered == []:
        print(f"ERROR! Host ID '{zhostid}' could not be find on Zabbix.")
        print(f"ERROR! Please check the host name on {zapi.url}\n")
        exit(1)

    for h in hosts_filtered:
        if h['hostid'] == zhostid:
            host_name = h['host']
    
    #print("Host name match: ", host_name)
    
    return host_name


def get_groupname(zapi, zgroupid):
    """
	TODO: write docstrings
	"""

    print(f"Getting group ID {zgroupid} from Zabbix API...\n")
    groups_filtered = zapi.hostgroup.get(output="extend", filter={"groupid": zgroupid})
    print(f"Groups got from Zabbix API: {groups_filtered}")
    if groups_filtered == []:
        print(f"ERROR! Group ID '{zgroupid}' could not be find on Zabbix.")
        print(f"ERROR! Please check the group name on {zapi.url}\n")
        exit(1)

    for g in groups_filtered:
        if g['groupid'] == zgroupid:
            group_name = g['name']
    
    print("Group name match: ", group_name)
    
    return group_name


def get_groupid(zapi, group_name):
    """
	TODO: write docstrings
	"""

    groups_filtered = zapi.hostgroup.get(output="extend", filter={"name": group_name})
    #print(f"Groups got: {groups_filtered}\n")

    if groups_filtered == []:
        print(f"ERROR! Group '{group_name}' could not be find on Zabbix.")
        print(f"ERROR! Please check the group names on {zapi.url}\n")
        exit(1)

    for g in groups_filtered:
        if g['name'] == group_name:
            groupid = g['groupid']
    
    return groupid
        

def get_hostinterfaceid(zapi, host_name):
    """
	TODO: write docstrings
	"""

    zhostid = get_hostid(zapi, host_name)
    print(f"Getting host interface of host {host_name} from Zabbix API...\n")
    interfaces_filtered = zapi.hostinterface.get(output="extend", filter={"hostids": zhostid})
    #print(f"Host interfaces got from Zabbix API: {interfaces_filtered}")
    if interfaces_filtered == []:
        print(f"ERROR! Host interfaces of host '{host_name}' could not be find on Zabbix.")
        print(f"ERROR! Please check the host name and its interfaces on {zapi.url}")
        exit(1)

    for i in interfaces_filtered:
        if i['hostid'] == zhostid:
            iid_updated = i['interfaceid']
    
    #print("Hostinterface match: ", iid_updated)
    
    return iid_updated


def update_host_name(zapi, host_name, new_name):
    """
	TODO: write docstrings
	"""

    zhostid = get_hostid(zapi, host_name)
    try:
        zapi.host.update(
            hostid=zhostid, 
            name=new_name
        )
        print(f"Visible Name of host '{host_name}' changed to '{new_name}'\n")
        print("")
        sleep(5)
    except Exception as e:
        print(e)
        exit(1)

    return


def update_hostinterface(zapi, host_name, new_ip):
    """
	TODO: write docstrings
	"""

    zhostinterfaceid = get_hostinterfaceid(zapi, host_name)
    try:
        zapi.hostinterface.update(
            interfaceid=zhostinterfaceid, 
            ip=new_ip
        )
        print(f"IP address of host '{host_name}' changed to '{new_ip}'\n")
        print("")
        sleep(5)
    except Exception as e:
        print(e)
        exit(1)

    return


def remove_hostgroup_from_host(zapi, zhostname, zgroupname):
    """
	TODO: write docstrings
	"""

    zhostid = get_hostid(zapi, zhostname)
    zgroupid = get_groupid(zapi, zgroupname)
    try:
        zapi.hostgroup.massremove(
            groupids=[
                zgroupid
            ],
            hostids= [
                zhostid
            ]
        )
        print(f"Host '{zhostname}' removed from hostgroup name '{zgroupname}' ID '{zgroupid}'\n")
    except Exception as e:
        print(e)

    return


def add_hostgroup_to_host(zapi, zhostname, zgroupname):
    """
	TODO: write docstrings
	"""
    
    zhostid = get_hostid(zapi, zhostname)
    zgroupid = get_groupid(zapi, zgroupname)
    try:
        zapi.hostgroup.massadd(
            groups=[
                {
                    "groupid": zgroupid
                }
            ],
            hosts= [
                {
                    "hostid": zhostid
                }
            ]
        )
        print(f"Host '{zhostname}' added to hostgroup name '{zgroupname}' ID '{zgroupid}'\n")
        sleep(5)
    except Exception as e:
        print(e)