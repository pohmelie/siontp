import re
import pathlib
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


BASE_PATH = pathlib.Path(__file__).parent
try:
    version = re.findall(r"""^__version__ = "([^']+)"\r?$""",
                         (BASE_PATH / "siontp" / "__init__.py").read_text(),
                         re.M)[0]
except IndexError:
    raise RuntimeError("Unable to determine version.")


setup(
    name="siontp",
    version=version,
    description=("Simple sans-io ntp client with sync and async backend"),
    long_description=(BASE_PATH / "README.md").read_text(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    author="pohmelie",
    author_email="multisosnooley@gmail.com",
    url="https://github.com/pohmelie/siontp",
    license="Apache 2",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "aiohttp": ["aiohttp"],
        "requests": ["requests"],
    },
    include_package_data=True,
)
