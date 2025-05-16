# tests/conftest.py
import os, sys
# Add the parent directory of this tests folder into Python’s import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
