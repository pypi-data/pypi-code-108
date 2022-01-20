"""Command line entrypoint for shui application"""
from cleo import Application
from shui.commands import InstallCommand, VersionsCommand

application = Application("shui", "0.1.0", complete=True)
application.add(InstallCommand())
application.add(VersionsCommand())


def main():
    """Command line entrypoint for shui application"""
    application.run()
