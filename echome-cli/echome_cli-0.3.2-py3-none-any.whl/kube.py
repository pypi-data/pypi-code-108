import sys
import argparse
import json
from echome import Session
from echome.kube import Kube
from .base_service import BaseService
from .defaults import APP_NAME

class KubeService(BaseService):

    description = "Create and manage Kubernetes clusters."

    def __init__(self):
        self.parent_service = "kube"
        self.parent_full_name = "Kubernetes"

        self.table_headers = ["Cluster ID",  "Controller", "Associated Instances", "Status", "Created"]
        self.data_columns=["cluster_id", "primary", ["associated_instances", "instance_id"], "status", "created"]

        self.session = Session()
        self.client:Kube = self.session.client("Kube")

        self.parent_service_argparse()


    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('cluster_id',  help='Cluster Id', metavar="<cluster-id>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        clusters = self.client.describe_cluster(args.cluster_id)
        if args.output == "table":
            self.print_table(clusters["results"])
        elif args.output == "json":
            print(json.dumps(clusters, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all Kubernetes clusters', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        clusters = self.client.describe_all_clusters()
        if args.output == "table":
            self.print_table(clusters["results"])
        elif args.output == "json":
            print(json.dumps(clusters, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def terminate(self):
        parser = argparse.ArgumentParser(description='Terminate a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('cluster_id',  help='Cluster Id', metavar="<cluster-id>")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.terminate_cluster(args.cluster_id))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def get_config(self):
        parser = argparse.ArgumentParser(description='Obtain the Kubernetes Admin config file', prog=f"{APP_NAME} {self.parent_service} get-config")
        parser.add_argument('cluster_id',  help='Cluster Id', metavar="<cluster-id>")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--file',  help='Where a new file will be created with the contents of the config file.', metavar="<./cluster.conf>")
        group.add_argument('--no-file',  help='Output only the config file to stdout instead of into a file.', action='store_true')

        args = parser.parse_args(sys.argv[3:])

        try:
            kube_config = self.client.get_kube_config(args.cluster_id)['results']['admin.conf']
        except Exception:
            print("There was an error when attempting to retrieve the config file.")
            exit(1)

        if args.no_file:
            print(kube_config)
            exit(0)
        else:
            try:
                with open(args.file, "a") as file_object:
                    file_object.write(kube_config)
            except Exception as error:
                print(error)
                exit(1)
        
        exit()
    

    def create(self):
        parser = argparse.ArgumentParser(description='Create a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--image-id', help='Image Id', required=True, metavar="<value>", dest="ImageId")
        parser.add_argument('--instance-type', help='Instance Size', required=True, metavar="<value>", dest="InstanceType")
        parser.add_argument('--network-profile', help='Network type', required=True, metavar="<value>", dest="NetworkProfile")
        parser.add_argument('--controller-ip', help='IP address of the primary controller', required=True, metavar="<value>", dest="ControllerIp")
        parser.add_argument('--key-name', help='Key name', metavar="<value>", dest="KeyName")
        parser.add_argument('--disk-size', help='Disk size', metavar="<value>", dest="DiskSize")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.create_cluster(**vars(args)))
        
        #TODO: Return exit value if command does not work
        exit()
