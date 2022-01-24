"""
Main CLI entrypoint.
"""
import sys


def print_info() -> None:
    """
    Print package info to stdout.
    """
    print(
        "Type annotations for boto3.Route53RecoveryReadiness 1.20.42\n"
        "Version:         1.20.42\n"
        "Builder version: 6.3.2\n"
        "Docs:            https://pypi.org/project/mypy-boto3-route53-recovery-readiness/\n"
        "Boto3 docs:      https://boto3.amazonaws.com/v1/documentation/api/1.20.42/reference/services/route53-recovery-readiness.html#Route53RecoveryReadiness\n"
        "Other services:  https://pypi.org/project/boto3-stubs/\n"
        "Changelog:       https://github.com/vemel/mypy_boto3_builder/releases"
    )


def print_version() -> None:
    """
    Print package version to stdout.
    """
    print("1.20.42")


def main() -> None:
    """
    Main CLI entrypoint.
    """
    if "--version" in sys.argv:
        return print_version()
    print_info()


if __name__ == "__main__":
    main()
