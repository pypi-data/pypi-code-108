from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

packages = ['flask_jobs']
print('packages=', packages)

setup(
    name="flask_jobs",

    version="1.0.14",
    # 1.0.14 - Added app.jobs.Find() and app.jobs.FindAll()
    # 1.0.13 - Added callbacks for job success and failure
    # 1.0.10 - Added Job.dict() to cast job object as json-able dict
    # 1.0.9 - Buf fix, when calling GetJob(), the Job['status'] was incorrectly forced to 'pending' even if it was previously complete
    # 1.0.8 - Bug fix, when timer.start() throws a 'cant start new thread' error
    # 1.0.7 - Added deleteOldJobs to specify whether old/completed jobs should be kept in the database
    # 1.0.3 - Bug fix - Creating duplicate cron jobs. Now ensures one unique job per host
    # 1.0.0 - Moved to using python-crontab on linux, seems to be working well (fingers crossed)
    # 0.0.23 - Added JobScheduler.SetLogger()
    # 0.0.20 - Added app.teardown to kill worker thread
    # 0.0.19 - added app.jobs.RefreshWorker() in case worker dies unexpectedly (it shouldnt.... shouldnt)
    # 0.0.18 - changed init_app so that it doesnt override the app.db

    packages=packages,
    install_requires=['flask_dictabase', 'python_crontab'],

    # metadata to display on PyPI
    author="Grant miller",
    author_email="grant@grant-miller.com",
    description="An easy job scheduling interface for flask projects.",
    long_description=long_description,
    license="PSF",
    keywords="flask job scheduler apscheduler celery redis crontab cron job ",
    url="https://github.com/GrantGMiller/flask_jobs",  # project home page, if any
    project_urls={
        "Source Code": "https://github.com/GrantGMiller/flask_jobs",
    }
)

# to push to PyPI

# test postgres: 'postgres://xfgkxpzruxledr:5b83aece4fbad7827cb1d9df48bf5b9c9ad2b33538662308a9ef1d8701bfda4b@ec2-35-174-88-65.compute-1.amazonaws.com:5432/d8832su8tgbh82'
# python -m setup.py sdist bdist_wheel
# twine upload dist/*
