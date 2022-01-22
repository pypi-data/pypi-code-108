import os
import traceback


class JobPlugin:
    """
    PlugInInterface
    """
    exec_dir = ""
    version = 1

    def __set_exec_dir(self, name):
        path = f'./' + name
        if not os.path.exists(path):
            os.makedirs(path)
        self.exec_dir = path

    def execution(self, **kwargs):
        print("'execution' method not implemented")

    def run(self, job_id, plugin_args: dict = None):

        res = {"job_id": job_id, "status": "pending", "plugin": self.__class__.__name__.__str__(), 'error': ""}
        self.__set_exec_dir(job_id)
        try:
            self.execution(**plugin_args)
            res["status"] = "success"
            self.res = res
            self.finish()
            self.clean()
        except Exception as e:
            res["status"] = 'failure'
            res["error"] = str(e)
            print(traceback.format_exc())
            self.rollback()

        finally:
            return res

    def rollback(self):
        print("'rollback' method not implemented")

    def clean(self):
        print("'rollback' method not implemented")

    def finish(self):
        print("'finish' method not implemented")


if __name__ == '__main__':
    pass
