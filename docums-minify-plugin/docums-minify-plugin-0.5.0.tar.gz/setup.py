from setuptools import setup, find_packages

setup(
    name='docums-minify-plugin',
    version='0.5.0',
    description='An Docums plugin to minify HTML, JS or CSS files prior to being written to disk',
    long_description='',
    keywords='docums minify publishing documentation html css',
    url='https://github.com/khanhduy1407/docums-minify-plugin',
    author='NKDuy',
    author_email='kn145660@gmail.com',
    license='MIT',
    python_requires='>=3.0',
    install_requires=[
        'docums>=1.0.0',
        'htmlmin>=0.1.4',
        'jsmin>=3.0.0',
        'csscompressor>=0.9.5',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(),
    entry_points={
        'docums.plugins': [
            'minify = docums_minify_plugin.plugin:MinifyPlugin'
        ]
    }
)
