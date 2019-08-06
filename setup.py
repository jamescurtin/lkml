from pathlib import Path
from setuptools import setup, find_packages
from codecs import open

__version__ = "0.2.0"

here = Path(__file__).parent.resolve()

# Get the long description from the README file
with (here / "README.md").open(encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="lkml",
    version=__version__,
    description="A speedy LookML parser implemented in pure Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joshtemple/lkml",
    download_url="https://github.com/joshtemple/lkml/tarball/" + __version__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
    ],
    keywords="lookml looker parser",
    license="MIT",
    entry_points={"console_scripts": ["lkml = lkml.__init__:cli"]},
    packages=find_packages(exclude=["docs", "tests*", "scripts"]),
    include_package_data=True,
    author="Josh Temple",
    tests_require=["pytest"],
    author_email="",
)
