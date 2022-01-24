from setuptools import setup, find_packages


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.txt').read()

setup(
  name='hek',
  version='0.1.9',
  description='A python library mostly used for pentesting and automation some tasks.',
  long_description=long_description,
  url='https://github.com/greedalbadi/hek',
  author='greed albadi',
  author_email='greedalbadi@gmail.com',
  license='MIT',
  keywords=["python", "pentesting", "automation", "stream", "http"],
  packages=find_packages(),
  install_requires=['pillow', "psutil", "requests", "requests[socks]",
                    "numpy", "pyautogui", "datetime", "opencv-python"
                    ]
)