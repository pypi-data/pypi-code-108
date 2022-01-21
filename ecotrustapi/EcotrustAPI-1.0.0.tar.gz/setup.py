from setuptools import setup

descricao_longa = """
    // TODO
"""

setup(
    name="EcotrustAPI",
    version="1.0.0",
    install_requires=[
        'requests', 'urllib3'
    ],
    description="Biblioteca para interação com API do EcotrustET",
    long_description=descricao_longa,
    author="EcoIT - Dev Team",
    author_email="pablo.viana@ecoit.com.br",
    py_modules=['ecotrust_api'],
    python_requires='>=3.9',
)