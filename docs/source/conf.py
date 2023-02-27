# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'py-drivesdk'
copyright = '2022, HHG-TecLap'
author = 'HHG-TecLap'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'enum_tools.autoenum'
]

templates_path = ['_templates']
exclude_patterns = []

# Allow for compiling the docs without installing the library first
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
autodoc_mock_imports = ["bleak"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']