from .fs import add, get, ls, rm
from .auth import get_master_key, set_master_key, get_client, set_client
from getpass import getpass
from argparse import ArgumentParser

def main():
    try:
        get_master_key()
    except:
        print("ERROR: No master key")
        print("Please enter a secure password. This will be used to encrypt the file data when stored on Discord.")
        set_master_key()
    
    try:
        get_client()
    except:
        print("ERROR: Discord client connection failed")
        print("Please enter bot information.")
        token = getpass("Bot token: ")
        fchan = input("File channel ID: ")
        lchan = input("Listing channel ID: ")
        set_client(token, fchan, lchan)
    
    commands = {
        "add": add,
        "get": get,
        "ls": ls,
        "rm": rm
    }
    
    parser = ArgumentParser()
    parser.add_argument("command", help="add (Add file), get (Download file), ls (List files), rm (Delete file)")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--out", "-o", help="Location to save downloaded file")
    args = parser.parse_args()
    
    if args.command not in commands:
        print(f"Invalid command: {args.command}")
        parser.print_help()
        exit(1)
    
    for file in args.files:
        commands[args.command](file, out=args.out)
    
    if args.command == "ls":
        ls()