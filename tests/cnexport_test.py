import sys, os
sys.path.insert(0, os.path.abspath('..'))
from io import open
import unittest
import argparse
import os
import shutil
import logging
import mock
logger = logging.getLogger()
logger.setLevel(40)

from src import cnExport, model

TEST_CNEXPORT_DIR = './dirmodule'

def setUp():
    try :
        os.makedirs(TEST_CNEXPORT_DIR)
    except :
        pass

class CnExportTestCase(unittest.TestCase):

    def test_writeHtml(self):
        html = u"<p>Text</p>"
        m = 'module'
        cnExport.writeHtml(m, TEST_CNEXPORT_DIR, html)
        self.assertTrue(os.path.isdir(TEST_CNEXPORT_DIR))
        self.assertTrue(os.path.exists(TEST_CNEXPORT_DIR+'/'+m+'.html'))
        html_file = open(TEST_CNEXPORT_DIR+'/'+m+'.html')
        lines = html_file.readlines()
        self.assertTrue(html in lines[0])

    def test_processModule(self):
        # SET UP
        parser = argparse.ArgumentParser(description="Parses markdown files and generates a website using index.tmpl in the current directory. Default is to process and all folders 'module*'.")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-m", "--modules", help="module folders", nargs='*')
        parser.add_argument("-l", "--log", dest="logLevel",
                            choices=['DEBUG', 'INFO', 'WARNING',
                                     'ERROR', 'CRITICAL'],
                            help="Set the logging level", default='WARNING')
        parser.add_argument("-r", "--repository",
                            help="Set the repository source dir containing the moduleX dirs, given as absolute or relative to cn_app dir",
                            default='repositories/culturenumerique/cn_modules')
        parser.add_argument("-d", "--destination",
                            help="Set the destination dir",
                            default='build')
        parser.add_argument("-u", "--baseUrl",
                            help="Set the base url for absolute url building",
                            default='http://culturenumerique.univ-lille3.fr')
        parser.add_argument("-f", "--feedback",
                            action='store_true',
                            help="Add feedbacks for all questions in web export",
                            default=False)
        parser.add_argument("-i", "--ims",
                            action='store_true',
                            help="Also generate IMS archive for each module",
                            default=False)
        parser.add_argument("-e", "--edx",
                            action='store_true',
                            help="Also generate EDX archive for each module",
                            default=False)

        args = parser.parse_args(['--edx', '--ims'])
        # with open("coursTest/module1/module_test.md", encoding='utf-8') as sample_file:
        #     m = model.Module(sample_file, "tests", "http://culturenumerique.univ-lille3.fr")
        #     objct = cnExport.processModule(args, './coursTest', './dirmodule', './module1')
        #     self.assertTrue(os.path.isdir('./dirmodule/module1'))
        #     self.assertTrue(os.path.isdir('./dirmodule/media'))
        #     self.assertTrue(os.path.exists('./dirmodule/module1.questions_bank.gift.txt'))




# Main
if __name__ == '__main__':
    setUp()
    unittest.main(verbosity=1)
