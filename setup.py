from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import glob
import os
import pkg_resources

from cov-support import __version__, _program


setup(name='cov-support',
      version=__version__,
      packages=find_packages(),
      scripts=["cov-support/scripts/Snakefile",
      "cov-support/scripts/process_data_download.smk",
      "cov-support/scripts/build_cov-support.smk",
      "cov-support/scripts/train_pangoLEARN.smk",
      "cov-support/scripts/update_lineage_data.smk"],
      install_requires=[
            "biopython>=1.70",
            "dendropy>=4.4.0",
            "pytools>=2020.1",
            'pandas>=1.0.1',
            'pysam>=0.15.4',
            "scipy>=1.4.1",
            "numpy>=1.13.3"
        ],
        description='annotated global cov-support builder',
        url='https://github.com/cov-lineages/cov-support',
        author='cov-lineages organisation',
        author_email='aine.otoole@ed.ac.uk',
        entry_points="""
        [console_scripts]
        {program} = cov-support.command:main
        """.format(program = _program),
        include_package_data=True,
        keywords=[],
        zip_safe=False)
