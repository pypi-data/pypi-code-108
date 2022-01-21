import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vue_js_reverse",
    version="0.0.7",
    author="Cem Yildiz",
    author_email="cem.yildiz@ya.ru",
    description="Vue JS Reverse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/miklagard/vue-js-reverse",
    packages=setuptools.find_packages(),
    package_data={
        'vue_js_reverse': [
            'templates/vue_js_reverse/*',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
