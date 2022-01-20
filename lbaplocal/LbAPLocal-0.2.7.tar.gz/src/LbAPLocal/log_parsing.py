###############################################################################
# (c) Copyright 2020-2021 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from collections import Counter
from io import StringIO

import click
import consolemd
from LbAPCommon.validators import explain_log
from LbAPCommon.validators.logs import _spit_by_level


def show_log_advice(log_text, suppress=5):
    log_messages = _spit_by_level(log_text)

    _show_message_summary(log_messages, "FATAL", fg="red", bold=True)
    _show_message_summary(log_messages, "ERROR", fg="red")
    _show_message_summary(log_messages, "WARNING", min_count=5, fg="yellow")
    click.echo()

    explanations, suggestions, errors = explain_log(log_text)

    if errors:
        click.secho("Errors have been detected!", fg="red", bold=True)
        _show_advice(errors)

    if suggestions:
        click.secho("Advice about warnings and errors:", fg="yellow")
        _show_advice(suggestions)

    if explanations:
        click.secho("General explanations", fg="green")
        _show_advice(explanations)

    if log_messages["FATAL"] or errors:
        raise click.ClickException("Found issues in log")


def _show_message_summary(log_messages, level, *, min_count=0, **formatting):
    total_count = len(log_messages[level])
    if not total_count:
        return
    messages = sorted(
        Counter(message for line_no, _, _, _, message in log_messages[level]).items(),
        key=lambda x: x[1],
        reverse=True,
    )
    click.secho(f"    Found {total_count} {level} message(s)", **formatting)
    n_supressed = 0
    n_supressed_unique = 0
    for message, count in messages:
        if count >= min_count:
            click.echo(f'        * {count} instances of "{message}"')
        else:
            n_supressed_unique += 1
            n_supressed += count
    if n_supressed:
        click.echo(
            f"        and {n_supressed} other(s) ({n_supressed_unique} unique). "
            'Pass "--suppress=0" to show all messages'
        )


def _show_advice(advice):
    for message, lines in advice:
        if lines is None:
            heading = "  * No line information available"
        else:
            heading = "  * Line" + ("s" if len(lines) > 1 else "") + ":"
            heading += f" {', '.join(map(str, lines[:5]))}"
            if len(lines) > 5:
                heading += f" and {len(lines) - 5} other(s)"
        click.secho(heading, fg="cyan")

        rendered_message = StringIO()
        consolemd.Renderer().render(message, output=rendered_message)
        click.echo("    " + rendered_message.getvalue().replace("\n", "\n    "))
