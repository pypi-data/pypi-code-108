import click

from eztea.sql._cli import main as sql_command


@click.group("eztea")
def main():
    """EZTea Web Framework"""


main.add_command(sql_command)

if __name__ == "__main__":
    main()
