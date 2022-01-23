from setuptools import setup, find_packages


setup(
    name='youtube-analysis',
    version='0.2',
    license='MIT',
    author="Dinesh Ram",
    author_email='dineshramdsml@gmail.com',
    packages=find_packages(),
    url='https://github.com/dineshram0212/youtube-analysis',
    keywords='youtube analysis',
    install_requires=[
          'pandas', 'seaborn', 'matplotlib', 'google-api-python-client'
      ],

)