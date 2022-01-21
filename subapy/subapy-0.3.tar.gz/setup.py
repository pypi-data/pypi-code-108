from distutils.core import setup
setup(
    name='subapy',
    packages=['subapy'],
    version='0.3',
    license='MIT',
    description='Supabase API Wrapper',
    author='FishballNoodles',
    author_email='joelkhorxw@gmail.com',
    url='https://github.com/TheReaper62/Subapy',
    download_url='https://github.com/TheReaper62/Subapy/archive/refs/tags/v0.3.tar.gz',
    keywords=['supabase', 'api', 'wrapper','database','db'],
    install_requires=[
        'requests',
        'asyncio'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)