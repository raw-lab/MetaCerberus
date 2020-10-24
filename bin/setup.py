import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RoboMax",
    version="0.8",
    author="Alexander Brown, Richard White",
    author_email="raw937@gmail.com",
    description="python code for versatile Functional Ontology Assignments for Metagenomes via Hidden Markov Model (HMM) searching with environmental focus of shotgun meta'omics data",
    long_description=long_description,
    url="https://github.com/raw937/robomax",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6.9',
    install_requires=[
          'setuptools',
          'scikit-bio',
          'dask',
          'pandas',
          'numpy',
          'humanize',
          'plotly',
          'psutil',
          'joblib',
          'hmmer @ http://eddylab.org/software/hmmer/hmmer.tar.gz',
          'prokka @ https://github.com/tseemann/prokka/tarball/master'
          ],
)
