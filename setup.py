from setuptools import setup
import re


with open('src/xman/__init__.py') as f:
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Version not found!")


with open('src/requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='xMan',
    version=version,
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
