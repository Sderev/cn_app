 #!/usr/bin/ python
# -*- coding: utf-8 -*-

from io import open
import json
import unittest
from collections import namedtuple
from StringIO import StringIO
from jinja2 import Template, Environment, FileSystemLoader
# Path hack for getting access to src python modules
import sys, os
sys.path.insert(0, os.path.abspath('..'))

# Ignore Warning
import logging
logger = logging.getLogger()
logger.setLevel(40)

from src import model,utils
