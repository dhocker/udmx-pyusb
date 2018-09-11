# pyuDMX.py - Anyma (and clones) uDMX interface module
# Copyright (C) 2016  Dave Hocker (email: AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE file).  If not, see <http://www.gnu.org/licenses/>.
#
# To build distribution:
# python setup.py sdist
#
# To install distribution in current venv:
#   pip install -U dist/pyudmx-x.y.z.tar.gz
# where x.y.z is the version number (e.g. 1.0.0)
#

import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='udmx-pyusb',
    version='2.0.0',
    description='uDMX Interface Library',
    long_description=(read('Readme.md')),
    long_description_content_type="text/markdown",
    url='https://www.github.com/dhocker/udmx-pyusb',
    license='GPLv3. See LICENSE file.',
    author='Dave Hocker',
    author_email='AtHomeX10@gmail.com',
    py_modules=[],
    include_package_data=True,
    packages=find_packages(exclude=['tests*']),
    install_requires=['pyusb>=1.0.2'],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
