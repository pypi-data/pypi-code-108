import sys
import argparse
import json
from echome import Session
from echome.identity import Identity
from base_service import BaseService
from defaults import APP_NAME

class IdentityService(BaseService):
    
    description = "Create and manage User accounts, tokens, and policies."

    def __init__(self):
        self.parent_service = "identity"
        self.parent_full_name = "Identity"

        self.table_headers = ["Username", "First Name", "Last Name", "User ID", "Active", "Created"]
        self.data_columns=["username", "first_name", "last_name", "user_id", "is_active", "created"]

        self.session = Session()
        self.client:Identity = self.session.client("Identity")

        self.parent_service_argparse()


    def describe_user(self):
        parser = argparse.ArgumentParser(description='Describe a specific user', prog=f"{APP_NAME} {self.parent_service} describe-user")
        parser.add_argument('username',  help='Username or user id', metavar="<username>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.describe_user(args.username)
        self.print_output(users["results"], args.output)
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_all_users(self):
        parser = argparse.ArgumentParser(description='Describe all users', prog=f"{APP_NAME} {self.parent_service} describe-all-users")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.describe_all_users()
        self.print_output(users["results"], args.output)
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_caller(self):
        parser = argparse.ArgumentParser(description='Describe caller', prog=f"{APP_NAME} {self.parent_service} describe-caller")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.describe_caller()
        self.print_output(users["results"], args.output)
        
        #TODO: Return exit value if command does not work
        exit()
    

    def create_user(self):
        parser = argparse.ArgumentParser(description='Create user or API keys', prog=f"{APP_NAME} {self.parent_service} create-user")
        parser.add_argument('--username', help='Username. This will be used for login.', required=True, metavar="<value>", dest="Username")
        parser.add_argument('--email', help='Email address of the user.', required=False, metavar="<value>", dest="Email")
        parser.add_argument('--name', help='Name of the user', required=False, metavar="<value>", dest="InstanceSize")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--password', help='Password for the user. If this is not supplied, the script will prompt you to\
            add one where it will be obscured. Using this flag means the password may be seen. If no password needs to be supplied,\
            use --no-password.', required=False, metavar="<value>", dest="Password")
        group.add_argument('--no-password',  help='No password will be passed. One will be generated for you.', action='store_true')

        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.create(**vars(args)))
        
        #TODO: Return exit value if command does not work
        exit()


    def delete_user(self):
        parser = argparse.ArgumentParser(description="Delete a user or a user's API keys", prog=f"{APP_NAME} {self.parent_service} delete-user")
        args = parser.parse_args(sys.argv[3:])

        results = self.client.delete()
        self.print_output(results, "json")
        
        #TODO: Return exit value if command does not work
        exit()
