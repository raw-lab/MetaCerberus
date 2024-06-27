# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MetaCerberus ReadTheDocs'
copyright = '2024, Jose L Figueroa III, Eliza Dhungel, Madeline Bellanger, Cory R Brouwer, Richard Allen White III.'
author = 'Jose L Figueroa III, Eliza Dhungel, Madeline Bellanger, Cory R Brouwer, Richard Allen White III.'
release = '29 February 2024'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_sidebars = {
   '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'],
   'index': [],
}


master_doc = 'index'
