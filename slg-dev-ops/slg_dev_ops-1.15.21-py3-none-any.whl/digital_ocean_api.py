# # Here make sure to update your Token and the other Droplet details like the region, your SSH key and etc.
# new_droplet=$(curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer b7d03a6947b217efb6f3ec3bd3504582" -d '{"name":"example.com","region":"nyc3","size":"s-1vcpu-1gb","image":"ubuntu-16-04-x64","ssh_keys":[107149],"backups":false,"ipv6":true,"user_data":null,"private_networking":null,"volumes": null,"tags":["web"]}' "https://api.digitalocean.com/v2/droplets")

# new_droplet_id=$(echo $new_droplet | jq .droplet.id)

# new_droplet_details=$(curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${api_key}" "https://api.digitalocean.com/v2/droplets/${new_droplet_id}")

# new_droplet_ip=$(echo $new_droplet_details | jq .droplet.networks.v4[].ip_address)

# echo "Your new Droplet's IP address is: ${new_droplet_ip}"

import requests
import json
from pprint import pprint
import time

from requests.api import delete

def list_all_droplets(do_token):
    resp = requests.get(
        f"https://api.digitalocean.com/v2/droplets",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        }
    )
    return resp

def create_droplet(
    do_token,
    name="ubuntu-20",
    size="s-1vcpu-1gb",
    image="ubuntu-20-04-x64",
    region="nyc1",
    tags=[],
    testing=False
):
    # returns droplet id
    SSH_FINGERPRINT="d6:f9:23:71:0a:1b:86:9e:39:cb:c2:89:49:23:65:1a"

    if testing:
        tags = tags + ["testing"]
        name = name + '-testing'
    resp = requests.post(f"https://api.digitalocean.com/v2/droplets",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        },
        json={
            "name": name,
            "region": region,
            "size": size,
            "image": image,
            "ssh_keys": [SSH_FINGERPRINT],
            "tags": tags
        }
    )
    if resp.status_code == 202:
        return resp.json()['droplet']['id']
    else:
        return False

def get_droplets_ip(droplet_id, do_token, max_retries=50):
    for i in range(max_retries):
        resp = requests.get(
            f"https://api.digitalocean.com/v2/droplets/{droplet_id}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {do_token}",
            }
        )
        ips = resp.json()['droplet']['networks']['v4']
        if len(ips) != 0:
            public = resp.json()['droplet']['networks']['v4'][0]
            if public['type'] == 'public':
                return public['ip_address']
            else:
                public = resp.json()['droplet']['networks']['v4'][1]
                if public['type'] == 'public':
                    return public['ip_address']
                else:
                    raise Exception(f'Unknown issue with getting IP for droplet "{droplet_id}"')
        print('IP not yet uploaded, trying again in 5 seconds...', flush=True)
        time.sleep(5)

    return False

def list_all_domain_records(domain_name, do_token):
    resp = requests.get(
        f"https://api.digitalocean.com/v2/domains/{domain_name}/records",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        }
    )
    if resp.status_code == 200:
        return resp.json()['domain_records']
    else:
        return resp

def delete_domain_record(domain_name, domain_record_id, do_token):
    resp = requests.delete(f"https://api.digitalocean.com/v2/domains/{domain_name}/records/{domain_record_id}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        }
    )
    return True if not resp.text else resp

def add_domain_records(
    droplet_ip,
    domain_name,
    do_token,
    type='A',
    names=['@', 'www', 'staging'],
    delete_existing_of_type=True,
):
    if delete_existing_of_type:
        domain_records = list_all_domain_records(domain_name, do_token)
        for domain in domain_records:
            if domain['type'] == type:
                delete_domain_record(domain_name, domain['id'], do_token)

    successfully_created = []
    for name in names:
        resp = requests.post(f"https://api.digitalocean.com/v2/domains/{domain_name}/records",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {do_token}",
            },
            json={
                "type": type,
                "name": name,
                "data": droplet_ip,
            }
        )
        if resp.status_code == 201:
            successfully_created.append(name)
    return f'Successfully created records for {", ".join(successfully_created)}'

def list_all_firewalls(do_token):
    resp = requests.get(
        f"https://api.digitalocean.com/v2/firewalls",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        }
    )
    return resp

def apply_firewall_to_droplet(droplet_id, do_token, firewall_id='015f2518-25a2-4d9d-914e-525483d817fc'):
    resp = requests.post(f"https://api.digitalocean.com/v2/firewalls/{firewall_id}/droplets",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        },
        json={
            "droplet_ids": [droplet_id],
        }
    )
    return True if not resp.text else resp

def destroy_droplet(droplet_id, do_token):
    resp = requests.delete(f"https://api.digitalocean.com/v2/droplets/{droplet_id}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        }
    )
    return True if not resp.text else resp

def destroy_testing_droplets(do_token):
    resp = requests.delete(f"https://api.digitalocean.com/v2/droplets?tag_name=testing",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {do_token}",
        }
    )
    return True if not resp.text else resp
