from setuptools import setup, find_packages
import os

setup(
    name="PyCheer",
    version="1.2.5",
    author="cyrxdzj",
    author_email="cyrxdzj@qq.com",
    url="https://gitee.com/cyrxdzj/PyCheer",
    long_description="Please see https://gitee.com/cyrxdzj/PyCheer",
    packages=[
        'PyCheer',
    ],
    package_dir={'PyCheer': 'PyCheer'},
    package_data={
        'PyCheer': ['html/*.html', 'js/*.js', 'js/theme/*.js', 'js/mode/*.js', 'css/*.css', 'logo/*', 'language/*.json',
                    'lottie/*.json']
    },
    license="MulanPSL-2.0",
    zip_safe=False,
    keywords='PyCheer',
    entry_points={
        'console_scripts': [
            'pycheer=PyCheer:main_function',
            'PyCheer=PyCheer:main_function'
        ]
    },
    install_requires=[
        "flask",
        "GitPython"
    ]
)

if os.environ.get("HOME"):
    language_path = os.path.join(os.environ.get("HOME"), ".PyCheer/language").replace("\\", "/")
else:
    language_path = os.path.join(os.environ.get("APPDATA"), "PyCheer/language").replace("\\", "/")
if not os.path.exists(language_path):
    os.makedirs(language_path)

for i in os.listdir("./PyCheer/language"):
    infobj = open(os.path.join("./PyCheer/language", i), encoding="utf-8")
    outfobj = open(os.path.join(language_path, i), "w", encoding='utf-8')
    outfobj.write(infobj.read())
    infobj.close()
    outfobj.close()
