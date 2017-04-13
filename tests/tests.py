#!/usr/bin/python
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

from src import model,utils

"""
    Test File for Project Esc@pad
    ==============================

    Here is a test file to test the project Esc@pad.
    This file test :
        - Parsing of source files to construct a course model (cf model.Module) with module_test.md ( the file to file) and test.config.json() (the serialized control object)
        - ( #TODO à remplir)
        -
        -

    How to use this file ?
    ---------------------
    In your terminal, use the command :
        >> $ python tests.py


"""


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
        self.assertEqual(self.control_module.author, self.sample_module.author, "Not the same author")
        self.assertEqual(self.control_module.menutitle, self.sample_module.menutitle, "Not the same menutitle")
        self.assertEqual(self.control_module.language, self.sample_module.language, "Not the same language")
        self.assertEqual(self.control_module.css, self.sample_module.css, "Not the same CSS")
        self.assertEqual(self.control_module.title, self.sample_module.title, "Not the same title")
        print("[ModuleParsingTestCase]-- Parsing Header OK --")


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
        #check header parsing
        self.check_headers_parsing()
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

class FctParserTestCase(unittest.TestCase):
    """

    """
    # def JSON_string_header(author, base_url, css, language, menutitle, module, title):
    #     return ("{'author': '"+author+"', 'base_url': '"+base_url+"', 'css':'"+css+"', 'language': '"+language+"','menutitle': '"+menutitle+"','module': '"+module+"','title': '"+title+"' }")

    def check_default_parser_head(self):
        # JSON control
        object_header = StringIO("""
        {
        "author": "culture numerique",
        "base_url": "http://culnu.fr",
        "css": "http://culturenumerique.univ-lille3.fr/css/base.css",
        "language": "fr",
        "menutitle": "Titre",
        "module": "culnu",
        "title": "Titre long"
        }
        """)
        control_header = json.load(object_header, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        del object_header

        # Parsed MD without header
        pars_head = StringIO("""
        # Titre 1
        """)
        sample_object = model.Module(pars_head, "culnu", "http://culnu.fr")
        sample_object.toHTML(False)
        sample_header = json.loads(sample_object.toJson(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        del sample_object

        #Test the default value of metadata
        self.assertEqual(control_header.title, sample_header.title, "Not the same title in default_parser_head")
        self.assertEqual(control_header.author, sample_header.author, "Not the same author in default_parser_head")
        self.assertEqual(control_header.base_url, sample_header.base_url, "Not the same base_url in default_parser_head")
        self.assertEqual(control_header.css, sample_header.css, "Not the same css in default_parser_head")
        self.assertEqual(control_header.language, sample_header.language, "Not the same language in default_parser_head")
        self.assertEqual(control_header.menutitle, sample_header.menutitle, "Not the same menutitle in default_parser_head")
        self.assertEqual(control_header.module, sample_header.module, "Not the same module in default_parser_head")
        print("[FctParserTestCase]-- default_parser_head OK --")


    def runTest(self):
        self.check_default_parser_head()


# Main
if __name__ == '__main__':
    unittest.main(verbosity=1)
