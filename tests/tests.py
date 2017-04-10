#!/usr/bin/python
# -*- coding: utf-8 -*-

from io import open
import json
import unittest
from collections import namedtuple
from jinja2 import Template, Environment, FileSystemLoader
# Path hack for getting access to src python modules
import sys, os
sys.path.insert(0, os.path.abspath('..'))

from src import model


class ModuleParsingTestCase(unittest.TestCase):
    """ Here we only test if the parsing works right and ends up with a correct module object.
        Does not treat the generation of IMS or EDX archive """

    def setUp(self):
        """ Build up control_module from tests.config.json file and sample_module from parsing of module_test.md"""
        #self.longMessage=True # for more verbose exception messages
        with open('tests.config.json', encoding='utf-8') as jsf:
            self.control_module = json.load(jsf, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

        with open("module_test.md", encoding='utf-8') as sample_file:
            self.sample_object = model.Module(sample_file, "tests", "http://culturenumerique.univ-lille3.fr")
            self.sample_object.toHTML(False)
            # outfile = open('sample.config.json', 'wb')
            # outfile.write(self.sample_object.toJson())
            self.sample_module = json.loads(self.sample_object.toJson(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            del self.sample_object

    # def tearDown(self):
    #
    #     self.control_module = None
    #     self.sample_module = None

    def check_number_of_sections(self):
        """for  sample module 'sample_m', match the number of sections with control module 'control_m'"""
        self.assertEqual(len(self.control_module.sections),len(self.sample_module.sections), "Not the same number of sections")
        print("[ModuleParsingTestCase]-- Number of sections OK --")


    def check_headers_parsing(self):
        """Check if info placed in the header of test md file gets correctly parsed"""
        pass


    def check_subsections(self):
        """Loop through all subsections and check
            we catch and keep each type of exception to separate checks
        """
        typeMatchingError = None
        srcSplitError = None
        htmlSrcMatchingError = None
        for i,sec in enumerate(self.sample_module.sections):
            for j,sub in enumerate(sec.subsections):
                self.assertIsNotNone(self.control_module.sections[i].subsections[j], "actual subsection out of bound for sec[%d].sub[%d]" % (i,j))
                control_sub = self.control_module.sections[i].subsections[j]
                # Compare type stored in 'folder' attribute
                try:
                    self.assertEqual(sub.folder,control_sub.folder, "no matching type for sec[%d].sub[%d]" % (i,j))
                except AssertionError as typeMatchingError:
                    pass
                # Compare src
                try:
                    self.assertMultiLineEqual(sub.src,control_sub.src,"src string do not match for sec[%d].sub[%d]" % (i,j))
                except AssertionError as srcSplitError:
                    pass
                # Compare html_src FIXME: should make separate test for all output generation testing HTML | IMS | EDX
                try:
                    self.assertEqual(sub.html_src,control_sub.html_src, "html src do not match for sec[%d].sub[%d]" % (i,j)) #FIXME : use a xml_based comparison
                except AssertionError as htmlSrcMatchingError:
                    pass
        if not typeMatchingError:
            print("[ModuleParsingTestCase]-- Subsections types OK --")
        else:
            raise typeMatchingError
        if not srcSplitError:
            print("[ModuleParsingTestCase]-- Subsections split OK --")
        else:
            raise srcSplitError
        if not htmlSrcMatchingError:
            print("[ModuleParsingTestCase]-- Subsections html_src OK --")
        else:
            raise htmlSrcMatchingError

    def runTest(self):
        #check number of sections
        self.check_number_of_sections()
        #check subsections are splited right and with right types
        self.check_subsections()
        #Module object exact match
        self.assertEqual(self.control_module, self.sample_module, msg="Module objects do not match exactly")
        print("[ModuleParsingTestCase]-- Exact match OK --")


class HtmlGenerationTestCase(ModuleParsingTestCase):
    """ Basic class for testing output generation in HTML """
    def setUp(self):
        super(HtmlGenerationTestCase, self).setUp()
        # then build html output for control and sample
        # module_template = jenv.get_template("module.html")
        # module_html_content = module_template.render(module=module)
        # html = site_template.render(course=course_obj, module_content=module_html_content, body_class="modules", logo=logo)
        # utils.write_file(html, os.getcwd(), outDir, module.module+'.html')

    def runTest(self):
        print("[HtmlGenerationTestCase] (nothing) OK")




# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
