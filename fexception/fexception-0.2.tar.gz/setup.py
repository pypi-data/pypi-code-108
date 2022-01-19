from setuptools import setup

if __name__ == "__main__":
    try:
        setup()
    except:  # noqa
        print(
            "\n\nAn error occurred while building the fexception project.\n\n"
            "Please check that your setuptools version is up to date.\n"
            "Verify Command: pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
