#!/usr/bin/env python

from distutils.core import setup

setup(
    name="arrsync",
    version="0.2",
    description="A tool to sync Sonarr, Radarr, and Lidarr",
    install_requires=[
        "requests>=2.22",
        "pydantic>=2.5",
    ],
    packages=["arrsync"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": ["arrsync=arrsync.__main__:main"],
    },
)
