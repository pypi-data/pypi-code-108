#!/usr/bin/env python3.8

import typer

import helpo.cloudflarecmd as cloudflarecmd
import helpo.dediboxcmd as dediboxcmd
import helpo.jiracmd as jiracmd
import helpo.namedotcomcmd as namedotcomcmd
import helpo.remoteservercmd as remoteservercmd
import helpo.rundeckjobscmd as rundeckjobscmd

app = typer.Typer(no_args_is_help=True)
app.add_typer(cloudflarecmd.app, name="cloudflare", no_args_is_help=True)
app.add_typer(namedotcomcmd.app, name="namecom", no_args_is_help=True)
app.add_typer(jiracmd.app, name="jira", no_args_is_help=True)
app.add_typer(dediboxcmd.app, name="dedibox", no_args_is_help=True)
app.add_typer(remoteservercmd.app, name="remoteserver", no_args_is_help=True)
app.add_typer(rundeckjobscmd.app, name="rundeckjobs", no_args_is_help=True)
if __name__ == "__main__":
    app()
