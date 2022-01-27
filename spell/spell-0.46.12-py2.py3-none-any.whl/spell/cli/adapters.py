import platform
import sys

import click
from requests.adapters import HTTPAdapter

from spell.version import __version__ as CLI_VERSION
from spell import deployment_constants


UPDATE_MESSAGE = (
    "Your Spell CLI version {} is below the minimum recommended version of {}. " "Please upgrade by running: "
)


class UpdateNoticeAdapter(HTTPAdapter):
    """Print a one-time notice if responses from the Spell API say there are CLI updates available."""

    def __init__(self, *args, **kwargs):
        super(UpdateNoticeAdapter, self).__init__(*args, **kwargs)
        self.printed_notice = False

    def add_headers(self, request, **kwargs):
        user_agent = request.headers.get("User-Agent", "")
        if "SpellCLI" not in user_agent:
            user_agent = "SpellCLI/{version} ({system} {release}) {user_agent}".format(
                version=CLI_VERSION,
                system=platform.system(),
                release=platform.release(),
                user_agent=user_agent,
            ).strip()
        if "Python" not in user_agent:
            user_agent = "{user_agent} Python/{major}.{minor}.{patch}".format(
                user_agent=user_agent,
                major=sys.version_info.major,
                minor=sys.version_info.minor,
                patch=sys.version_info.micro,
            ).strip()
        request.headers["User-Agent"] = user_agent
        return super(UpdateNoticeAdapter, self).add_headers(request, **kwargs)

    def build_response(self, request, response):
        minimum_cli_version = response.headers.get("Spell-CLI-Update")
        if minimum_cli_version and not self.printed_notice:
            package_id = "spell"
            if deployment_constants.on_prem:
                latest_cli_filename = response.headers.get("Spell-CLI-Filename")
                package_id = latest_cli_filename
            self.print_update_notice(minimum_cli_version, package_id)
        return super(UpdateNoticeAdapter, self).build_response(request, response)

    def print_update_notice(self, version, package_id):
        message = UPDATE_MESSAGE.format(CLI_VERSION, version, package_id)
        if sys.stderr.encoding.lower() == "utf-8":
            text = click.wrap_text(message, initial_indent="✨ ", subsequent_indent="✨ ")
            text += "\n✨   pip install --upgrade {}".format(package_id)
        else:
            text = click.wrap_text(message)
            text += "\n   pip install --upgrade {}".format(package_id)
        click.echo(text, err=True)
        self.printed_notice = True
