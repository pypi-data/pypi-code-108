# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).

from bamboolib import __widgets_version__


JUPYTERLAB_MANAGER_VERSION_MAPPING = {
    "1.0.x": "1.0",
    "1.1.x": "1.0",
    "1.2.x": "1.1",
    "2.x": "2.0",
}


class Version:
    """Helper class to work with version strings"""

    def __init__(self, version_string: str) -> None:
        version_parts = version_string.split(".")
        self.major = version_parts[0]
        self.minor = version_parts[1]
        self.major_minor = self.major + "." + self.minor


def install_nbextensions() -> None:
    """
    Installs the Jupyter Notebook extensions that are required for bamboolib
    """
    print("Trying to install bamboolib nbextension...")

    try:
        from notebook import nbextensions
    except ImportError:
        print(
            "Could not install bamboolib Jupyter Notebook extension because Jupyter Notebook is not available"
        )
        return

    extensions = ["bamboolib", "ipyslickgrid", "widgetsnbextension", "plotlywidget"]
    for extension in extensions:
        nbextensions.install_nbextension_python(extension, user=True)
        nbextensions.enable_nbextension_python(extension)

    print("Finished installing the bamboolib Jupyter Notebook nbextension")
    print("Please reload your Jupyter notebook browser window")


def install_labextensions() -> None:
    """
    Installs the Jupyter Lab extensions that are required for bamboolib
    """
    print("Trying to install bamboolib labextensions...")

    try:
        from jupyterlab import commands
    except ImportError:
        print(
            "Could not install bamboolib Jupyter Lab extension because Jupyter Lab is not available"
        )
        return

    def jupyterlab_version() -> str:
        return commands.get_app_info()["version"]

    def get_jupyterlab_version_pattern(version_object) -> str:
        major_minor_version = version_object.major_minor
        if major_minor_version == "1.0":
            return "1.0.x"
        elif major_minor_version == "1.1":
            return "1.1.x"
        elif major_minor_version == "1.2":
            return "1.2.x"

        major_version = version_object.major
        if major_version == "2":
            return "2.x"

        raise Exception(
            "bamboolib does not support JupyterLab version %s. bamboolib only supports JupyterLab>=1.0. If you have troubles, please reach out to support@8080labs.com"
            % version
        )

    def get_required_jupyterlab_manager_version(jl_version):
        jl_version_pattern = get_jupyterlab_version_pattern(jl_version)
        return JUPYTERLAB_MANAGER_VERSION_MAPPING[jl_version_pattern]

    def get_jupyterlab_version():
        version = jupyterlab_version()
        return Version(version)

    def get_required_plotly_version():
        from plotly import __version__

        return __version__

    extensions = [
        "ipyslickgrid",
        "plotlywidget@%s" % get_required_plotly_version(),
        "jupyterlab-plotly@%s" % get_required_plotly_version(),
        "bamboolib@%s" % __widgets_version__,
    ]

    # TODO: can this be removed altoghether because we now have ipywidgets>=7.6.*
    # as a requirement?
    jl_version = get_jupyterlab_version()
    if int(jl_version.major) < 3:
        # In JupyterLab 2 and below, we need to manually install the jupyterlab-manager
        # For JL3, we need ipywidgets 7.6.0 which depends on jupyter_widgets 1.0.0
        # which installs the jupyterlab-manager as a prebuilt lab extension
        jl_manager_version = (get_required_jupyterlab_manager_version(jl_version),)
        extensions.append("@jupyter-widgets/jupyterlab-manager@%s" % jl_manager_version)

    for extension in extensions:
        print("Installing %s: ..." % extension, end=" ")
        commands.install_extension(extension)
        print("done")

    print("Starting JupyterLab build. This may take a while ...")
    commands.build()
    print("Successfully built JupyterLab")
    print("")
    print("Please reload your Jupyter Lab browser window")


def install_extensions() -> None:
    """
    Installs the extensions that are required for bamboolib for both Jupyter Notebook and Lab
    """
    print(
        "Starting to install bamboolib extensions for Jupyter Notebook and Jupyter Lab"
    )
    print("")
    install_nbextensions()
    print("")
    install_labextensions()
    print("")
    print("Finished installing the bamboolib Jupyter extensions")
    print("Please reload your Jupyter notebook and/or Jupyter lab browser windows")
