# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../program"))
sys.path.insert(0, os.path.abspath("../../program/flutter"))
sys.path.insert(0, os.path.abspath("../../program/flutter/ezfzf"))


project = "nox-template"
copyright = "2023, briocheAF"
author = "briocheAF"
release = "v0.0.1"

# autodoc_default_flags = ['members']
# autodoc_decorators_preserve = True

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "recommonmark",
]

autodoc_mock_imports = ["../../noxfile.py"]


# Set the autodoc options
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

source_parsers = {".md": "recommonmark.parser.CommonMarkParser"}
