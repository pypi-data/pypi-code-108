import codefast as cf
import setuptools

setuptools.setup(
    name="dofast",
    version="1.0.2dev2",  # Latest version .
    author="GaoangLiu",
    author_email="byteleap@gmail.com",
    description="A package for dirty faster Python programming.",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/slipper",
    packages=setuptools.find_packages(),
    package_data={
        setuptools.find_packages()[0]: [
            "dofast.json.zip", 'data/vps_init.sh', 'data/*.txt', 'data/*.conf',
            'pyavatar/templates/*.svg', 'pyavatar/templates/**/*.svg',
            'pyavatar/templates/**/**/*.svg'
        ]
    },
    install_requires=[
        'codefast>=0.6.0', 'hashids', 'colorlog>=4.6.1', 'tqdm', 'joblib', 'PyGithub',
        'oss2', 'lxml', 'cos-python-sdk-v5', 'smart-open', 'pillow', 'bs4',
        'arrow', 'redis', 'termcolor', 'python-twitter', 'python-telegram-bot',
        'deprecation', 'faker', 'pynsq', 'flask', 'googletrans==3.1.0a0',
        "cairosvg >= 2.3.0", 'jinja2 >= 2.9.3', 'waitress', 'celery',
        'authc>=0.0.7', 'youtube-dl'
    ],
    entry_points={
        'console_scripts': [
            'sli=dofast.sli_entry:main', 'hint=dofast.sli_entry:_hint_wubi',
            'websurf=dofast.nsq.websurf:run', 'weather=dofast.weather:entry',
            'jsy=dofast.sli_entry:jsonify',
            'tgpostman=dofast.nsq.telegram_postman:daemon',
            'qflask=dofast.qflask:run', 'sn=dofast.sli_entry:nsq_sync',
            'syncfile=dofast.nsq.syncfile:daemon',
            'hemabot=dofast.sli_entry:hemabot', 'uu=dofast.ext.cli:app',
            'snc=dofast.ext.redis_sync:entry', 'msg=dofast.ext.redis_sync:msg',
            'vps_monitor=dofast.linux.vps:main',
            'pcloud_upload=dofast.web.pcloud:pcloud_upload_entry',
            'calculate_prime=dofast.nsq.calculate_prime:calculate_prime',
            'vvv=dofast.client:entry', 'slippervideo=dofast.cli.slippervideo:post_video_to_channel'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
