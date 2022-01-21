#Mikrotik to HTML Dumper
#2021 - Angelo Poggi : angelo.poggi@webair.com

import routeros_api
from json2html import *
from mt_html.creds import USERNAME, PASSWORD
from mt_html.dump_folder_gen import check_dump_folder
import sys
import click


def html_dump(firewall):
    """script that logs into a Mikrotik and creates a Mark down file so you can use it on a webpage"""
    click.echo(f"Connecting to {firewall}")
    connection = routeros_api.RouterOsApiPool(str(firewall), username=str(USERNAME),
                                              password=str(PASSWORD),
                                              plaintext_login=True,
                                              use_ssl=False,
                                              port=8728)
    try:
        api = connection.get_api()
    except Exception as e:
        click.echo(f'Something went wrong trying to connect: Error {e}')
        sys.exit(1)
    list_interface = api.get_resource('/interface')
    nat_rules = api.get_resource('/ip/firewall/nat')
    address_list = api.get_resource('/ip/firewall/address-list')
    firewall_rules = api.get_resource('/ip/firewall/filter')
    hostname = api.get_resource('/system/identity')
    system_id = api.get_resource('/system/license')
    ip_addr = api.get_resource('/ip/address')
    ipsec_peer = api.get_resource('/ip/ipsec/peer')
    ipsec_policy = api.get_resource('/ip/ipsec/policy')
    hostname_results = []
    for item in hostname.get():
        hostname_results.append({
            'hostname' : item.get('name', '')
        })
    ipsec_peer_results = []
    for item in ipsec_peer.get():
        ipsec_peer_results.append({
            'name': item.get('name', ''),
            'address': item.get('address', ''),
            'local-address': item.get('local-address', ''),
            'exchange-mode': item.get('exchange-mode', '')
        })
    ipsec_policy_results = []
    for item in ipsec_policy.get():
        ipsec_policy_results.append({
            'Peer': item.get('peer', ''),
            'src-address': item.get('src-address', ''),
            'dst-address': item.get('dst-address', ''),
            'sa-src-address': item.get('sa-src-address', ''),
            'sa-dst-address': item.get('sa-dst-address', '')
        })
    system_id_results = []
    for item in system_id.get():
        system_id_results.append({
            'system-id': item.get('system-id', 'N/A'),
            'software-id': item.get('software-id', 'N/A')
        })
    interface_results = []
    for item in list_interface.get():
        interface_results.append({
            'name': item.get('name', 'N/A'),
            'mac-address': item.get('mac-address', 'N/A'),
            'default-name': item.get('default-name', 'N/A')
        })
    nat_results = []
    for item in nat_rules.get():
        nat_results.append({
            'chain': item.get('chain', 'N/A'),
            'action': item.get('action', 'N/A'),
            'src-address': item.get('src-address', 'N/A'),
            'to-address': item.get('to-address', 'N/A'),
            'comment': item.get('comment', 'N/A')
        })
    result = []
    for item in firewall_rules.get():
        result.append({
            'chain': item.get("chain", "N/A"),
            'protocol': item.get("protocol", "N/A"),
            'src-address': item.get("src-address", "N/A"),
            'dst-address': item.get("dst-address", "N/A"),
            'comment': item.get("comment", "N/A"),
            'action': item.get("action", 'N/A')
        })
    address_list_results = []
    for item in address_list.get():
        address_list_results.append({
            'list': item.get("list", ""),
            'address': item.get("address", "N/A")
        })
    ip_addr_results = []
    for item in ip_addr.get():
        address_list_results.append({
            'Interface' : item.get('interface', ""),
            'Address' : item.get('address', "")
        })
    #Payloads
    peer_payload = json2html.convert(json=ipsec_peer_results)
    ip_addr_payload = json2html.convert(json=ip_addr_results)
    address_list_payload = json2html.convert(json=address_list_results)
    firewall_payload = json2html.convert(json=result)
    nat_payload = json2html.convert(json=nat_results)
    interface_payload = json2html.convert(json=interface_results)
    systemid_payload = json2html.convert(json=system_id_results)
    policy_payload = json2html.convert(json=ipsec_policy_results)
    hostname_payload = json2html.convert(json=hostname_results)

    click.echo(f'Creating File {firewall}.html')
    path = check_dump_folder()
    with open(f'{path}/{firewall}.html', 'w+') as doc_html:
        doc_html.write(f'<h1>{firewall}</h1>\n')
        doc_html.write(hostname_payload)
        doc_html.write(f'<h1>System ID</h1>\n')
        doc_html.write(systemid_payload)
        doc_html.write(f'<h1>Interfaces</h1>\n')
        doc_html.write(interface_payload)
        doc_html.write(f'<h1>IP addresses</h1>\n')
        doc_html.write(ip_addr_payload)
        doc_html.write(f'<h1>Filter Rules</h1>\n')
        doc_html.write(firewall_payload)
        doc_html.write(f'<h1>NAT</h1>\n')
        doc_html.write(nat_payload)
        doc_html.write(f'<h1>Address-Lists</h1>\n')
        doc_html.write(address_list_payload)
        doc_html.write(f'<h1>IPSec Phase 1</h1>\n')
        doc_html.write(peer_payload)
        doc_html.write(f'<h1>IPSec Phase 2</h1>\n')
        doc_html.write(policy_payload)
    click.echo('File Created, please copy & paste into Confluence')
    sys.exit(0)
