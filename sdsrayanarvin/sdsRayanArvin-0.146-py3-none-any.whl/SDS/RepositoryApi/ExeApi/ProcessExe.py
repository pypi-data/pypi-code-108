from sdsRayanArvin.Repository import Repository


class ProcessExe(Repository):
    def ProcessRunOnId(self, ID_process):
        res = self.Request.sendWithToken('GET', 'run/' + ID_process)
        return res['status']