import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cerberus",
    version="1.0",
    author="Richard White III, Jose Figueroa",
    author_email="rwhit101@uncc.edu",
    description="python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data",
    long_description=long_description,
    url="https://github.com/raw-lab/cerberus",
    package_dir={'': 'bin'},
    packages=['cerberus'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=[
          'setuptools',
          #'scikit-bio',
          #'pandas',
          #'numpy',
          #'humanize',
          #'plotly',
          #'psutil',
          #'joblib',
          ],
)
