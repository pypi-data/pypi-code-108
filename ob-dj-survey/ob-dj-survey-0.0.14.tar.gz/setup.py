from setuptools import find_packages, setup

setup(
    install_requires=["django", "djangorestframework",],
    # TODO: https://github.com/obytes/ob-dj-otp/issues/3
    packages=find_packages(
        include=[
            "ob_dj_survey.apis",
            "ob_dj_survey.apis.survey",
            "ob_dj_survey.core",
            "ob_dj_survey.core.survey",
            "ob_dj_survey.core.survey.migrations",
        ],
        exclude=["tests", "tests.*",],
    ),
    tests_require=["pytest"],
    use_scm_version={"write_to": "version.py",},
    setup_requires=["setuptools_scm"],
)
