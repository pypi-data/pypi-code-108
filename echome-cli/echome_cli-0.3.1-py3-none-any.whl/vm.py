import sys
import argparse
import json
from tabulate import tabulate
from echome import Session
from echome.vm import Vm
from .base_service import BaseService
from .defaults import APP_NAME

class VmService(BaseService):

    description = "Create and manage with ecHome virtual machines and images."

    exclusions = [
        "print_vm_table", 
        "print_image_table"
    ]

    def __init__(self):
        self.parent_service = "vm"
        self.parent_full_name = "Virtual Machine"
        
        self.session = Session()
        self.client:Vm = self.session.client("Vm")

        self.parent_service_argparse()
    

    def describe_all_vms(self):
        parser = argparse.ArgumentParser(description='Describe all virtual machines', prog=f"{APP_NAME} {self.parent_service} describe-all-vms")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        items = self.client.describe_all_vms()
        self.print_output(items["results"], args.output, self.print_vm_table)

        exit()
    

    def describe_vm(self):
        parser = argparse.ArgumentParser(description='Describe a virtual machine', prog=f"{APP_NAME} {self.parent_service} describe-vm")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        vm = self.client.describe_vm(args.vm_id)
        self.print_output(vm["results"], args.output, self.print_vm_table)
        
        exit()

    
    def create_vm(self):
        parser = argparse.ArgumentParser(description='Create a virtual machine', prog=f"{APP_NAME} {self.parent_service} create-vm")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--image-id', help='Image Id', metavar="<value>", dest="ImageId")
        group.add_argument('--volume-id', help='Volume Id', metavar="<value>", dest="VolumeId")
        parser.add_argument('--instance-type', help='Instance Size', required=True, metavar="<value>", dest="InstanceType")
        parser.add_argument('--network-profile', help='Network type', required=True, metavar="<value>", dest="NetworkProfile")
        parser.add_argument('--private-ip', help='Network private IP', metavar="<value>", dest="PrivateIp")
        parser.add_argument('--key-name', help='Key name', metavar="<value>", dest="KeyName")
        parser.add_argument('--disk-size', help='Disk size', metavar="<value>", dest="DiskSize")
        parser.add_argument('--disk-image-id', help='Disk Image to mount to the virtual machine', metavar="<value>", dest="DiskImageId")
        parser.add_argument('--name', help='Name of the instance', metavar="<value>", dest="Name")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        parser.add_argument('--enable-vnc', help='Enable VNC', action='store_true', dest="EnableVnc")
        parser.add_argument('--vnc-port', help='VNC port to use if enabled', metavar="<value>", dest="VncPort")
        parser.add_argument('--user-data-file', help='Add user data scripts to the cloud instance. This file does not need to be base64 encoded, the CLI will do this for you.', \
          metavar="./example-file.sh", dest="UserDataScript")
        args = parser.parse_args(sys.argv[3:])
        items = vars(args)

        if "UserDataScript" in items and items["UserDataScript"] != None:
            try:
                with open(items["UserDataScript"]) as f:
                    items["UserDataScript"] = f.read()
            except OSError as err:
                print(err)
                print("File Opening error!")
                exit(1)
        else:
            items.pop("UserDataScript", None)
        
        if "Name" in items and items["Name"] != None and items["Name"] != "":
            if items["Tags"] == None:
                items["Tags"] = {}
            items["Tags"]["Name"] = items["Name"]
            items.pop("Name", None)

        # ** unpacks the arguments, vars() returns the variables and provides them to client.create() as
        # ImageId=gmi-12345, InstanceSize=standard.small, etc.
        resp = self.client.create_vm(**items)
        self.print_output(resp, "json")
        #TODO: Return exit value if command does not work
        exit()
    

    def create_vm_image(self):
        parser = argparse.ArgumentParser(description='Create an image of an existing virtual machine', prog=f"{APP_NAME} {self.parent_service} create-vm-image")
        parser.add_argument('vm_id',  help='Existing Virtual Machine Id', metavar="<vm-id>")
        parser.add_argument('--name',  help='Name of the new image', metavar="<image-name>", dest="Name", required=True)
        parser.add_argument('--description',  help='Description of the new image', metavar="<image-desc>", dest="Description", required=True)
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        resp = self.client.create_vm_image(**vars(args))
        self.print_output(resp, "json")
        #TODO: Return exit value if command does not work
        exit()


    def start_vm(self):
        parser = argparse.ArgumentParser(description='Start a virtual machine', prog=f"{APP_NAME} {self.parent_service} start-vm")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        args = parser.parse_args(sys.argv[3:])

        resp = self.client.start_vm(args.vm_id)
        self.print_output(resp, "json")
        #TODO: Return exit value if command does not work
        exit()
    

    def stop_vm(self):
        parser = argparse.ArgumentParser(description='Stop a virtual machine', prog=f"{APP_NAME} {self.parent_service} stop-vm")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        args = parser.parse_args(sys.argv[3:])

        resp = self.client.stop_vm(args.vm_id)
        self.print_output(resp, "json")
        #TODO: Return exit value if command does not work
        exit()
    

    def terminate_vm(self):
        parser = argparse.ArgumentParser(description='Terminate a virtual machine', prog=f"{APP_NAME} {self.parent_service} terminate-vm")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        args = parser.parse_args(sys.argv[3:])

        resp = self.client.terminate_vm(args.vm_id)
        self.print_output(resp, "json")
        #TODO: Return exit value if command does not work
        exit()


    def register_guest_image(self):
        parser = argparse.ArgumentParser(description='Register an image', prog=f"{APP_NAME} {self.parent_service} register-guest-image")
        parser.add_argument('--image-path',  help='Path to the new image. This image must exist on the new server and exist in the configured guest images directory.', metavar="</path/to/image>", dest="ImagePath", required=True)
        parser.add_argument('--image-name',  help='Name of the new image', metavar="<image-name>", dest="ImageName", required=True)
        parser.add_argument('--image-description',  help='Description of the new image', metavar="<image-desc>", dest="ImageDescription", required=True)
        parser.add_argument('--image-user',  help='Default user for logging into the image', metavar="<image-user>", dest="ImageUser")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        resp = self.client.register_guest_image(**vars(args))
        self.print_output(resp, "json")

        #TODO: Return exit value if command does not work
        exit()
    

    def describe_guest_image(self):
        parser = argparse.ArgumentParser(description='Describe a guest image', prog=f"{APP_NAME} {self.parent_service} describe-guest-image")
        parser.add_argument('image_id',  help='Image Id', metavar="<image-id>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        image = self.client.describe_guest_image(args.image_id)
        self.print_output(image["results"], args.output, self.print_image_table)
        
        #TODO: Return exit value if command does not work
        exit()

    
    def describe_user_image(self):
        parser = argparse.ArgumentParser(description='Describe a user image', prog=f"{APP_NAME} {self.parent_service} describe-user-image")
        parser.add_argument('image_id',  help='Image Id', metavar="<image-id>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        image = self.client.describe_user_image(args.image_id)
        self.print_output(image["results"], args.output, self.print_image_table)
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_all_guest_images(self):
        parser = argparse.ArgumentParser(description='Describe all guest images', prog=f"{APP_NAME} {self.parent_service} describe-all-guest-images")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        images = self.client.describe_all_guest_images()
        self.print_output(images["results"], args.output, self.print_image_table)
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_all_user_images(self):
        parser = argparse.ArgumentParser(description='Describe all user images', prog=f"{APP_NAME} {self.parent_service} describe-all-user-images")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        images = self.client.describe_all_user_images()
        self.print_output(images["results"], args.output, self.print_image_table)
        
        #TODO: Return exit value if command does not work
        exit()


    def print_vm_table(self, vm_list, wide:bool = False):
        headers = ["Name", "Vm Id", "Instance Size", "State", "IP", "Image", "Created"]
        all_vms = []
        for vm in vm_list:
            name = vm["tags"]["Name"] if "Name" in vm["tags"] else ""
            isize = f"{vm['instance_type']}.{vm['instance_size']}"
            if vm["interfaces"]:
                ip = vm["interfaces"]["config_at_launch"]["private_ip"]
            else:
                ip = ""

            if vm['image_metadata']:
                image = "{} ({})".format(vm['image_metadata']['image_id'], vm['image_metadata']['image_name'])
            else:
                image = ""

            v = [name, vm["instance_id"], isize, vm["state"]["state"], ip, image, vm["created"]]
            all_vms.append(v)

        print(tabulate(all_vms, headers))
    

    def print_image_table(self, img_list, wide:bool = False):
        table_headers = ["Name", "Image Id", "Format", "State", "Description"]
        data_columns=["name", "image_id", ["metadata", "format"], "state", "description"]
        self.print_table(img_list, table_headers, data_columns)
