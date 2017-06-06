#!/usr/bin/env python3

"""
This file launches all the tests.

Source used :
    http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
"""

import os
import sys
sys.path.append('..')
from pygiftparser import parser as pygift
import src


os.system('python parsergift_test.py')
os.system('python model_test.py')
os.system('python edx_test.py')
os.system('python ims_test.py')
