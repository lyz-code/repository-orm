"""Python package building configuration."""

import re
from glob import glob
from os.path import basename, splitext
from subprocess import getoutput

from setuptools import find_packages, setup
from setuptools.command.install import install


# To remove when the PR is merged:
# * PostInstall
# * In build.yml pipeline
# * Add the requirement in setup.py
# * In Makefile
# ignore: cannot subclass install, has type Any. And what would you do?
class PostInstall(install):  # type: ignore
    """Install direct dependency.

    Pypi doesn't allow uploading packages with direct dependencies, so we need to
    install them manually.
    """

    def run(self) -> None:
        """Install dependencies."""
        install.run(self)
        print(getoutput("pip install git+git://github.com/lyz-code/deepdiff@master"))


# Avoid loading the package to extract the version
with open("src/repository_orm/version.py") as fp:
    version_match = re.search(r'__version__ = "(?P<version>.*)"', fp.read())
    if version_match is None:
        raise ValueError("The version is not specified in the version.py file.")
    version = version_match["version"]


with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="repository-orm",
    version=version,
    description=(
        "Library to ease the implementation of the repository pattern in "
        "Python projects."
    ),
    cmdclass={"install": PostInstall},
    author="Lyz",
    author_email="lyz-code-security-advisories@riseup.net",
    license="GNU General Public License v3",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/lyz-code/repository-orm",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"repository_orm": ["py.typed"]},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Natural Language :: English",
    ],
    install_requires=[
        "pydantic",
        "pypika",
        "pymysql",
        "tinydb",
        "tinydb_serialization",
        "yoyo-migrations",
    ],
)
