from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.startup import instrument_lfi_os


@catches_generic_exception(__name__, "Error starting agent")
def start_agent():
    from flask import __version__
    framework_details = {"app_framework": "Flask", "app_framework_version": __version__}

    if TCellAgent.startup(framework_details):
        from tcell_agent.instrumentation.flaskinst.routes import report_routes
        report_routes()
        instrument_lfi_os()
