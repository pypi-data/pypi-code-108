from setuptools import setup

setup(
    name='sdsRayanArvin',
    version='0.146',
    description='System data server',
    author='vahid heydari',
    url='https://hamgit.ir/v.heidary13/sds',
    packages=[
        'sdsRayanArvin',
        'sdsRayanArvin.RepositoryApi',
        'sdsRayanArvin.RepositoryApi.OldApi',
        'sdsRayanArvin.RepositoryApi.DataApi',
        'sdsRayanArvin.RepositoryApi.WorkflowApi',
        'sdsRayanArvin.RepositoryApi.RuleApi',
        'sdsRayanArvin.RepositoryApi.WeatherApi',
        'sdsRayanArvin.RepositoryApi.ExeApi',
        'sdsRayanArvin.RepositoryApi.LogApi',
        'sdsRayanArvin.Dataset',
        'sdsRayanArvin.Library',
    ],
)
