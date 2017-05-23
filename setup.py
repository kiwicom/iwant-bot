"""
Taken from
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import pathlib


SETUP_PY_DIRECTORY = pathlib.Path(__file__).resolve().parent

# Get the long description from the README file
with open(SETUP_PY_DIRECTORY / 'README.md', encoding='utf-8') as f:
    long_description = f.read()


with open(SETUP_PY_DIRECTORY / 'requirements.txt', encoding='utf-8') as f:
    requirements_file_lines = f.read().strip().splitlines()


setup(
    name='iwant_bot',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0',

    description='A sample Python project',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/kiwicom/iwant-bot',

    # Author details
    author='kiwi.com interns',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat :: Slack',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='slack chatbot',

    package_dir={"": "src"},
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages("src", exclude=['docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements_file_lines,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': ['pytest'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
    zip_safe=True,
)
