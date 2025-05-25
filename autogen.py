"""
Shim module to alias pyautogen to autogen for import resolution.
"""
import pyautogen as autogen
from pyautogen import *  # noqa

# Expose attributes
__all__ = getattr(autogen, '__all__', [])
