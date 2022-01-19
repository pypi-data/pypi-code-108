from setuptools import setup

setup(name='cosabot',
    version='0.0.4',
    description='Computer Optic Semantics',
    packages=['cosa'],
    author = 'Alfredo Lozano',
    author_email = 'lozanoa94@gmail.com',
    install_requires=[
   'scipy',
   'scikit-image',
   'scikit-learn',
   'numpy'
   ],
   zip_safe=False,
)
