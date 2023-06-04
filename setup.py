from setuptools import setup
from xman import __version__

with open('src/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='xMan',
    version=__version__,
    packages=['xman'],
    package_dir={'': 'src'},
    url='https://github.com/wolfhoundgelert/xman',
    license='BSD 3-clause',
    author='Andrei Polkanov',
    author_email='andrey.polkanoff@gmail.com',
    description='xMan - Experiment Manager, python library for effective management and organising '
                'experiments on thе Google Colab platform with sharing and running in parallel '
                'across different Colab accounts.',
    install_requires=requirements,
)

# TODO https://github.com/pypi/support/issues/2738
