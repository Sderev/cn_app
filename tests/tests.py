#!/usr/bin/python
# -*- coding: utf-8 -*-

from io import open
import json
import unittest
from collections import namedtuple
# Path hack.
import sys, os
sys.path.insert(0, os.path.abspath('..'))

from src import model

class ModuleParsingTestCase(unittest.TestCase):
    """ Here we only test if the parsing works right and ends up with a correct module object.
        Does not treat the generation of IMS or EDX archive """

    def setUp(self):
        self.longMessage=True
        with open('tests.config.json', encoding='utf-8') as jsf:
            self.control_module = json.load(jsf, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

        with open("module_test.md", encoding='utf-8') as sample_file:
            self.sample_object = model.Module(sample_file, "tests", "http://culturenumerique.univ-lille3.fr")
            self.sample_object.toHTML(False)
            outfile = open('sample.config.json', 'wb')
            outfile.write(self.sample_object.toJson())
            self.sample_module = json.loads(self.sample_object.toJson(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    def check_number_of_sections(self):
        """for  sample module 'sample_m', match the number of sections with control module 'control_m'"""
        self.assertEqual(len(self.control_module.sections),len(self.sample_module.sections), "Not the same number of sections")
        print("-- Number of sections OK --")

    def check_headers_parsing(self):
        pass


    def check_subsections_split_and_types(self):
        """Loop through all subsections and check types and source split
            we catch and keep each type of exception to separate checks
        """
        typeMatchingError = None
        srcSplitError = None
        for i,sec in enumerate(self.sample_module.sections):
            for j,sub in enumerate(sec.subsections):
                self.assertIsNotNone(self.control_module.sections[i].subsections[j], "actual subsection out of bound for sec[%d].sub[%d]" % (i,j))
                control_sub = self.control_module.sections[i].subsections[j]
                try:
                    self.assertEqual(sub.folder,control_sub.folder, "no matching type for sec[%d].sub[%d]" % (i,j))
                except AssertionError as typeMatchingError:
                    pass
                try:
                    self.assertMultiLineEqual(sub.src,control_sub.src,"src string do not match for sec[%d].sub[%d]" % (i,j))
                except Exception as srcSplitError:
                    pass
        if not typeMatchingError:
            print("-- Subsections types OK --")
        else:
            raise typeMatchingError
        if not srcSplitError:
            print("-- Subsections split OK --")
        else:
            raise srcSplitError

    def runTest(self):
        #check number of sections
        self.check_number_of_sections()
        #check subsections are splited right and with right types
        self.check_subsections_split_and_types()
        #Module object exact match
        self.assertEqual(self.control_module, self.sample_module,msg="Module objects do not match exactly")
        print("-- Exact match OK --")


# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
