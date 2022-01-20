from setuptools import setup, find_packages

install_requires = [
    "locust",
    "redis-py-cluster",
    'pluggy==0.13.1',
    "loguru",
    "dingtalkchatbot",
    "allure-pytest",
    "pytest-ordering",
    "pymysql",
    "json_tools",
    "pytest~=6.2.5",
    "pako~=0.3.1",
    "websocket-client",
    "Faker",
    "dynaconf",
]

packages = find_packages("src")

long_description = "1.标题根据标签个数显示标签,2.将多进程修改为多线程，3.每个数据的第一个json文件为基础文件"


setup(name='autoTestScheme',
      version='0.1.0.9',
      url='https://gitee.com/xiongrun/auto-test-scheme',
      author='wuxin',
      description='auto test scheme',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author_email='xr18668178362@163.com',
      install_requires=install_requires,
      project_urls={'Bug Tracker': 'https://gitee.com/xiongrun/auto-test-scheme/issues'},
      package_dir={'': 'src'},
      packages=packages,
      include_package_data=True,
      entry_points={'pytest11': ['pytest_autoTestScheme = autoTestScheme']},
      package_data={
          'demo': ['demo/*'],
          'autoTestScheme': ['allure/*'],
      },
      )
