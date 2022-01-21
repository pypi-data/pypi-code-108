#helps to create env file
#2021 - Angelo Poggi : angelo.poggi@webair.com
import click


def create_env_file():
    """Creates the .env file which stores the firewalls username and password"""
    username = input("please enter username\n")
    password = input("please enter password\n")
    with open('.env', 'w') as envFile:
        envFile.write(f'username={username}\n')
        envFile.write(f'password={password}\n')
    click.echo(".env file generated, you should now be able to run the script against a firewall!")