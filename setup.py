# -*- coding: UTF-8 -*-
# vim:ft=python:et:ts=4:sw=4:ai

from setuptools import setup, find_packages

setup(
    name="qtpst",
    version="0.1",
    description="PyQt5 based GUI for pst mail boxes",
    author="Dimitar Dimitrov",
    author_email="ddimitrov4217@outlook.com",
    url="",
    install_requires=[
        # "pyqt>=5.9",
        "readms>=0.1.dev",
        ],
    packages=find_packages(exclude=["ez_setup"]),
    package_data={'qtpst': ['images/*', ]},
    include_package_data=True,
    zip_safe=False,
)
