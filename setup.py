# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup, find_packages

projectName="shop_provision"
scriptFile="%s/%s.py" % (projectName,projectName)
description="Setuptools setup.py for shop_provision."


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open(scriptFile).read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name=projectName,
    packages=find_packages(),
    #add required packages to install_requires list
    #install_requires=["package","package2"]
    entry_points={
        "console_scripts": ['%s = %s.%s:main' % (projectName, projectName, projectName)]
        },
    version=version,
    description=description,
    long_description=long_descr,
    author="Bo Laurent",
    author_email="bo.laurent@canonical.com",
    url="",
    install_requires=[
        "zuora_restful_python==0.13-dev0"
    ],
    dependency_links=['https://github.com/bolaurent/zuora_restful_python/tarball/master#egg=zuora_restful_python-0.13-dev0'],
    license='MIT',
    #list of classifiers: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Development Status :: 1 - Planning',
                 'License :: OSI Approved :: MIT License',
                 'Environment :: Console',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3 :: Only'],
    )
