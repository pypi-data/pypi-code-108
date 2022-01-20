import os

from setuptools import setup, find_packages

setup(
    name="gitrics",
    description="Python package to generate metrics based off git usage.",
    long_description=open(os.path.join(os.getcwd(), "README.md")).read().strip(),
    long_description_content_type="text/markdown",
    version=open(os.path.join(os.getcwd(), "VERSION")).read().strip(),
    url="https://gitlab.com/lgensinger/gitrics",
    install_requires=[d.strip() for d in open(os.path.join(os.getcwd(), "requirements.txt")).readlines()],
    extras_require={
        "test": [d.strip() for d in open(os.path.join(os.getcwd(), "requirements-test.txt")).readlines()]
    },
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "generate-dependency-metadata=gitrics.bin.generate_dependency_metadata:main",
            "generate-group-blockers=gitrics.bin.generate_group_blockers:main",
            "generate-metadata=gitrics.bin.generate_metadata:main",
            "generate-user-activity=gitrics.bin.generate_user_activity:main",
            "generate-user-color=gitrics.bin.generate_user_color:main",
            "generate-user-connection=gitrics.bin.generate_user_connection:main",
            "generate-user-contribution=gitrics.bin.generate_user_contribution:main",
            "generate-user-data=gitrics.bin.generate_user_data:main",
            "generate-user-data-coverage=gitrics.bin.generate_user_data_coverage:main",
            "generate-user-languages=gitrics.bin.generate_user_languages:main",
            "generate-user-profile=gitrics.bin.generate_user_profile:main",
            "generate-user-project-membership=gitrics.bin.generate_user_project_membership:main",
            "generate-user-topics=gitrics.bin.generate_user_topics:main"
        ],
    }
)
