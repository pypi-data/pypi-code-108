from penvy.PenvyConfig import PenvyConfig
from benvy.BenvyConfig import BenvyConfig
from penvy.env.EnvInitRunner import EnvInitRunner
from benvy.container.dicontainer import Container


def main():
    configs = [
        PenvyConfig(),
        BenvyConfig(),
    ]

    runner = EnvInitRunner(configs, Container)
    runner.run()


if __name__ == "__main__":
    main()
