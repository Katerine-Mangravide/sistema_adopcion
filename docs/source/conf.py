# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django

# Añadir la carpeta principal del proyecto al path
sys.path.insert(0, os.path.abspath(r'C:\Users\kater\sistema_adopcion'))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_adopcion.settings')
django.setup()


project = 'sistema_adopcion'
copyright = '2025, katerine'
author = 'katerine'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]