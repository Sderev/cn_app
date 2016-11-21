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
        return len(self.control_module.sections) == len(self.sample_module.sections)

    def check_number_of_subsections(control_s, sample_s):
        """for  sample section 'sample_s', match the number of subsections with control section 'control_s'"""
        pass

    def check_subsections_split_and_types(self):
        """for  sample section 'sample_s', match the number of subsections with control section 'control_s'"""
        for i,sec in enumerate(self.sample_module.sections):
            for j,sub in enumerate(sec.subsections):
                control_sub = self.control_module.sections[i].subsections[j]
                if sub.folder != control_sub.folder:
                    return False
                if sub.src != control_sub.src:
                    return False
        return True

    def runTest(self):
        #check number of sections
        self.assertTrue(self.check_number_of_sections(), "Not the same number of sections")
        #check subsections are splited right and with right types
        self.assertTrue(self.check_subsections_split_and_types(), "One subsection split or type is not right")
        #Module object exact match
        self.assertEqual(self.control_module, self.sample_module,msg="Module objects do not match")



if __name__ == '__main__':
    unittest.main()

    # def test_config_json(self):
    #     test_json =
    #
    #     self.assertEqual(fun(3), 4)
