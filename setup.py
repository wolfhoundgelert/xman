from setuptools import setup

setup(
    name='xman',
    version='0.0.11',
    packages=['xman'],
    package_dir={'': 'src'},
    url='https://github.com/wolfhoundgelert/xman',
    license='BSD 3-clause',
    author='Andrei Polkanov',
    author_email='andrey.polkanoff@gmail.com',
    description='Experiment Manager (xman) [IN_PROGRESS]'
)

# TODO https://github.com/pypi/support/issues/2738



# TODO >>>>> support setting from setup.py
    # import re
    #
    # def get_current_version():
    #     with open('xman/__init__.py', 'r') as f:
    #         version_file = f.read()
    #     version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    #     if version_match:
    #         return version_match.group(1)
    #     raise RuntimeError("Unable to find version string in __init__.py")
    #
    # def get_updated_version():
    #     current_version = get_current_version()
    #     major, minor, patch = current_version.split('.')
    #     patch = int(patch) + 1
    #     return f"{major}.{minor}.{patch}"
    #
    # from setuptools import setup
    #
    # setup(
    #     name='xman',
    #     version=get_updated_version(),
    #     ...
    # )
