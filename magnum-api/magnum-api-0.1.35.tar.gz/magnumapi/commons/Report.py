import scooby


class Report(scooby.Report):
    """Class for custom scooby.Report."""

    def __init__(self, additional=None, ncol=3, text_width=80, sort=False) -> None:
        # Mandatory packages
        core = ['numpy', 'pandas', 'numpy', 'dataclasses', 'ipyaggrid', 'plotly', 'ipyaggrid', 'scrapbook', 'papermill',
                'scooby', 'ansys.mapdl.core', 'ansys.mapdl.reader']
        optional = ['matplotlib', 'coverage']

        scooby.Report.__init__(self,
                               additional=additional,
                               core=core,
                               optional=optional,
                               ncol=ncol,
                               text_width=text_width, sort=sort)
