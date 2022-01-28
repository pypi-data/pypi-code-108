from bx.command import Command
import tempfile


class ScanDatesCommand(Command):
    """Collect acquisition dates from imaging sessions.

    Usage:
     bx scandates <resource_id>
    """
    nargs = 1

    def __init__(self, *args, **kwargs):
        super(ScanDatesCommand, self).__init__(*args, **kwargs)

    def parse(self):
        id = self.args[0]  # should be a project or an experiment_id

        from bx.dcm import collect_scandates
        res = self.run_id(id, collect_scandates, max_rows=3)
        if len(res) == 1:
            print(res.iloc[0])
        else:
            if self.destdir is None:
                self.destdir = tempfile.gettempdir()
            self.to_excel(res)
