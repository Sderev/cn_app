 #!/usr/bin/ python
# -*- coding: utf-8 -*-

from io import open
import json
import shutil
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

from src import model,utils,toEDX,toIMS

TEST_EDX_DIR = "./testEDX"

class EDXArchiveTestCase(unittest.TestCase):

    def setUp(self):
        with open("coursTest/module1/module_test.md", encoding='utf-8') as sample_file:
            self.m = model.Module(sample_file, "tests", "http://culturenumerique.univ-lille3.fr")
            self.m.toHTML()
            self.m_json = json.loads(self.m.toJson(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            if os.path.isdir(TEST_EDX_DIR):
                shutil.rmtree(TEST_EDX_DIR)
            (self.m).edx_archive_path = toEDX.generateEDXArchive(self.m, TEST_EDX_DIR)


    def runEDX(self):
        pass


    def runTest(self):
        self.runEDX()


# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
