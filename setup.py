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
    scripts=['bin/cerberus.py', 'bin/cerberusDB.py', 'bin/cerberus-slurm.sh'],
    package_dir={'': 'lib'},
    packages=['cerberus'],
    package_data={"":["*.py"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='==3.7.*',
    install_requires=[
            'setuptools',
            'ray',
            'configargparse',
            'scikit-learn',
            'pandas',
            'numpy',
            'plotly',
            'psutil',
            ],
)
