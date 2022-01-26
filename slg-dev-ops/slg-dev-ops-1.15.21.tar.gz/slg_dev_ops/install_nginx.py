import os
import argparse


def install_nginx(os_='ubuntu', codename='bionic', start=True):
    os.system('sudo touch /etc/apt/sources.list.d/nginx.list')
    os.system("sudo sed -i '/^/d' /etc/apt/sources.list.d/nginx.list")
    os.system(
        f"sudo bash -c \"echo 'deb http://nginx.org/packages/mainline/{os_}/ {codename} nginx' >> /etc/apt/sources.list.d/nginx.list\"")
    os.system(
        f"sudo bash -c \"echo 'deb-src http://nginx.org/packages/mainline/{os_}/ {codename} nginx' >> /etc/apt/sources.list.d/nginx.list\"")
    os.system('wget https://nginx.org/keys/nginx_signing.key')
    os.system('sudo apt-key add nginx_signing.key')
    os.system('sudo apt-get update')
    os.system('sudo apt-get install -y nginx')

    if start:
        os.system('sudo /etc/init.d/nginx start')

# The file you just created instructs the advanced package tool (APT) package management system to utilize the Official NGINX package repository. Modifying the file to provide the correct endpoint and code name for your distribution ensures that the APT utility receives the correct .deb packages for your system. The following commands download the NGINX GPG package signing key and import it into APT. Providing APT trhe signing key enables the APT system to validate packages from the repository. The apt-get update command instructs the APT system to refresh its package listings from its known repositories. After the package list is refreshed, you can install NGINX Open Source from the Official NGINX repository. After you install it, the final command starts NGINX.
