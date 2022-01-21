import click
from mt_html.env_creator import create_env_file
from dotenv import load_dotenv,find_dotenv, dotenv_values

env_file = find_dotenv(filename='.env')
if env_file is None:
    click.echo(".env file seems to be missing\n Lets generate a new one!")
    create_env_file()
    env_file = find_dotenv(filename='.env')
    env_creds = dotenv_values(env_file)
    USERNAME = env_creds['username']
    PASSWORD = env_creds['password']
else:
    try:
        env_creds = dotenv_values(env_file)
        USERNAME = env_creds['username']
        PASSWORD = env_creds['password']
    except:
        print("something went wrong opening ENV File - generating new one")
        create_env_file()