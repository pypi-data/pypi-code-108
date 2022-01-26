import subprocess

import click


@click.command()
@click.option('-p', '--part', 'part', required=True, type=str)
@click.option('-c', '--count', 'count', required=False, type=int, default=1)
def run(part: str, count: int) -> None:
    for _ in range(count):
        subprocess.check_output(f"bump2version --allow-dirty --current-version \"$(python setup.py --version)\" --parse '(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)(\\.dev(?P<dev>\\d+))?' --serialize '{{major}}.{{minor}}.{{patch}}.dev{{dev}}' --serialize '{{major}}.{{minor}}.{{patch}}' {part} setup.py", stderr=subprocess.STDOUT, shell=True)

if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
