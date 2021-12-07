import os
import setuptools

# development install (just creates links)
#pip install -e /home/jlfiguer/raw-lab/cerberus/
# install from local git repo (uses latest commit)
#pip install git+file:///home/jlfiguer/raw-lab/cerberus/
# install from git using pip
#pip install git+https://github.com/raw-lab/cerberus/
# build .tar.gz and .whl files in dist/
#python3 -m build
# install from build (avoids commit requirement for testing)
#pip install dist/*.whl

# recursively load package files
def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

# read long description
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cerberus",
    version="0.1",
    author="Jose Figueroa, Richard White III",
    author_email="jlfiguer@uncc.edu",
    description="Versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raw-lab/cerberus",
    scripts=['bin/cerberus-pipeline.py', 'bin/cerberus_setup.sh', 'bin/cerberus_slurm.sh'], # scripts to copy to 'bin' path
    packages=['cerberus', 'cerberus_data'], # list of packages, installed to site-packages folder
    package_dir=dict(cerberus='cerberus', cerberus_data='cerberus_data'), # dict with 'package'='relative dir'
    package_data=dict(cerberus_data=package_files('cerberus_data')), # add non-python data to package, relative paths
    #package_data=dict(cerberus_data=['*.fna', '*.json', '*.config', '*.css', 'FGS+','plotly-2.0.0.min.js']), # add non-python data to package, relative paths
    license="MIT License", # metadata
    platforms=['Unix'], # metadata
    classifiers=[ # This is the new updated way for metadata, but old way seems to still be used in some of the output
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='==3.7.*',
    install_requires=[
            'setuptools',
            'ray[default]',
            'metaomestats',
            'configargparse',
            'kaleido',
            'scikit-learn',
            'pandas',
            'numpy',
            'plotly',
            'psutil',
            'dominate',
            ],
)
