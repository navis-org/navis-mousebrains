from setuptools import setup, find_packages

import re

VERSIONFILE = "mousebrains/__version__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [l for l in requirements if l and not l.startswith('#')]

setup(
    name='mousebrains',
    version=verstr,
    packages=find_packages(),
    license='GNU GPL V3',
    description='Transforms to map between different mouse (template) brains',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/navis/navis-mousebrains',
    author='Philipp Schlegel',
    author_email='pms70@cam.ac.uk',
    keywords='mouse brains template registration brain navis transform',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=requirements,
    extras_require={'extras': []},
    python_requires='>=3.9',
    zip_safe=False,

    include_package_data=True

)
