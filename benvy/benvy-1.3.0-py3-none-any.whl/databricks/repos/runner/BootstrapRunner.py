from penvy.env.EnvInitRunner import EnvInitRunner


class BootstrapRunner(EnvInitRunner):
    def run(self):
        self._setup_runner.run()
