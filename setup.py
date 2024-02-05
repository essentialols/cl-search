from __future__ import annotations

from setuptools import find_packages
from setuptools import setup

setup(
    name="cl_search",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["cl=cl_search.main:main"],
    },
)
