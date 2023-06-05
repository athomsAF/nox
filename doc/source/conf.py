import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../src"))
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path)

PROJECT = os.getenv("GITHUB_REPOSITORY")
copyright =os.getenv("COPYRIGHT")
AUTHOR = os.getenv("GITHUB_USER")
RELEASE = os.getenv("REELEASE_PROJECT_VERSION")
autosectionlabel_prefix_document = True


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "myst_parser",
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.mermaid",
    # "sphinx-autodoc2"    #https://myst-parser.readthedocs.io/en/latest/syntax/code_and_apis.html#sphinx-autodoc2
]

autodoc_mock_imports = ["../../noxfile.py"]


# Set the autodoc options
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "reference-labels": True,
}
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

myst_enable_extensions = {
    "colon_fence": True,
    "substitution": True,
    "deflist": True,
    "dollarmath": True,
    "amsmath": True,
    "smartquotes": True,
    "replacements": True,
    "html_image": True,
    "html_admonition": True,
    "attrs_inline": True,
}

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
source_parsers = {".md": "recommonmark.parser.CommonMarkParser"}
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

source_parsers = {".md": "recommonmark.parser.CommonMarkParser"}

