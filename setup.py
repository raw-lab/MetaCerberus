import os
import setuptools


# recursively load package files
def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.py'):
                paths.append(os.path.join('..', path, filename))
    return paths

# read long description
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MetaCerberus",
    version="1.2.1",
    author="Jose L. Figueroa III, Richard A. White III",
    author_email="jlfiguer@uncc.edu",
    description="Versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raw-lab/metacerberus",
    scripts=['bin/metacerberus.py',                                     # scripts to copy to 'bin' path
             'bin/ray-slurm-metacerberus.sh',
             'bin/pathview-metacerberus.R'],
    packages=['meta_cerberus'],                                         # list of packages, installed to site-packages folder
    package_dir=dict(meta_cerberus='lib'),                              # dict with 'package'='relative dir'
    package_data=dict(meta_cerberus=package_files('lib/')),             # add non-python data to package, relative paths
    license="BSD License",  # metadata
    platforms=['Unix'],     # metadata
    classifiers=[           # This is the new updated way for metadata, but old way seems to still be used in some of the output
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.8',
    install_requires=[
            'setuptools',
            'ray',
            'metaomestats',
            'configargparse',
            'kaleido',
            'scikit-learn',
            'pandas',
            'plotly',
            'psutil',
            'dominate',
            ],
)
