import setuptools

setuptools.setup(
    name="hof",
    author="prs-watch",
    version="0.0.4",
    description="not practical tool to make hof as you want.",
    url="https://github.com/prs-watch/hof",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires = [
        "pybaseball", "click", "rich", "pandas"
    ],
    entry_points={
        "console_scripts": [
            "hof = hof:hof"
        ]
    }
)