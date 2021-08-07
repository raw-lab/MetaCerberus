import setuptools

#pip install -e /home/jlfiguer/raw-lab/cerberus/
#pip install git+file:///home/jlfiguer/raw-lab/cerberus/
#pip install git+https://github.com/raw-lab/cerberus/
#python3 -m build


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
    scripts=['bin/cerberus-pipeline.py', 'bin/cerberus_setup.sh', 'bin/cerberusDB.py', 'bin/cerberus_slurm.sh'],
    packages=['cerberus', 'cerberus_data'],
    package_dir=dict(cerberus='lib', cerberus_data='data'),
    package_data=dict(cerberus_data=['*.fna', '*.json', '*.config', 'plotly-2.0.0.min.js']),
    classifiers=[
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
            'scikit-learn',
            'pandas',
            'numpy',
            'plotly',
            'psutil',
            ],
)
