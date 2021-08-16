#!/usr/bin/env python
import codecs
import os
import re
from setuptools import setup, find_packages


def abspath(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


def get_contents(*args):
    with codecs.open(abspath(*args), "r", "utf-8") as handle:
        return handle.read()


def get_version(*args):
    contents = get_contents(*args)
    metadata = dict(re.findall(r'__([a-z]+)__\s+=\s+[\'"]([^\'"]+)', contents))
    return metadata["version"]


def read_requirements(*args):
    with open(abspath(*args), "r") as file:
        for line in file.readlines():
            if not line:
                continue
            yield line.strip()


def list_pyfiles(*args):
    path = abspath(*args)
    for file in os.listdir(path):
        file = os.path.join(path, file)
        if not os.path.isfile(file) or not file.endswith(".py"):
            continue
        yield file


setup(
    name="pyscreen",
    version=get_version("pyscreen", "__init__.py"),
    description="Extensible script to run a screen on your device (i.e. RPI via GPIO)",
    url="https://github.com/g0dsCookie/pyscreen",
    author="g0dsCookie",
    author_email="g0dscookie@copr.icu",
    license="MIT",
    packages=["pyscreen", "pyscreen.internal"],
    data_files=[
        ("share/pyscreen/plugins", list(list_pyfiles("pyscreen", "plugins")))
    ],
    entry_points=dict(console_scripts=["pyscreen = pyscreen.cli:main"]),
    install_requires=list(read_requirements("requirements.txt")),
    extras_require={
        "kubernetes": list(read_requirements("requirements_k8s.txt")),
    }
)