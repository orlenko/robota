"""Sphinx configuration."""
project = "Robota"
author = "Vlad Orlenko"
copyright = "2023, Vlad Orlenko"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
