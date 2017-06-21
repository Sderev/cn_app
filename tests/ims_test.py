#!/usr/bin/python
# coding: utf8


from io import open
import json
import mock

from lxml import etree
import shutil
from bs4 import BeautifulSoup
import unittest
from collections import namedtuple
from six.moves import StringIO
from jinja2 import Template, Environment, FileSystemLoader
# Path hack for getting access to src python modules
import sys, os
sys.path.insert(0, os.path.abspath('..'))

# Ignore Warning
import logging
logger = logging.getLogger()
logger.setLevel(40)

from pygiftparser import parser as pygift

from src import model, toIMS, fromGift

TEST_IMS_DIR = "./IMS"

def setUp():
    """
    Build IMS folder based on coursTest
    """
    with open("coursTest/module1/module_test.md", encoding='utf-8') as sample_file:
        global m
        m = model.Module(sample_file, "tests", "http://culturenumerique.univ-lille3.fr")
        m.toHTML()
        m_json = json.loads(m.toJson(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        if os.path.isdir(TEST_IMS_DIR):
            shutil.rmtree(TEST_IMS_DIR)
        m.ims_archive_path = toIMS.generateImsArchive(m, "Test", "./")
        sample_file.close()
        del m_json,sample_file

class IMSArchiveTestCase(unittest.TestCase):

    def testCreationDossierIMS(self):
        """
        Check if all directories and files are created
        """
        self.assertTrue(os.path.isdir(TEST_IMS_DIR),"dir "+TEST_IMS_DIR+" don't exist")
        self.assertTrue(os.path.exists('./'+'./Test.imscc.zip'), "imscc.zip don't exist")
        self.assertTrue(os.path.isdir(TEST_IMS_DIR+'/Activite'), "dir Activite don't exist")
        self.assertTrue(os.path.isdir(TEST_IMS_DIR+'/ActiviteAvancee'), "dir ActiviteAvancee don't exist")
        self.assertTrue(os.path.isdir(TEST_IMS_DIR+'/Comprehension'), "dir Comprehension don't exist")
        self.assertTrue(os.path.isdir(TEST_IMS_DIR+'/webcontent'), "dir webcontent don't exist")
        self.assertTrue(os.path.exists(TEST_IMS_DIR+'/imsmanifest.xml'), "file imsmanifest.xml don't exist")
        print("[IMSArchiveTestCase]-- check_creation_dossier_ims OK --")

    def testNbWebContent(self):
        """
        """
        list_files_html = os.listdir(TEST_IMS_DIR+'/webcontent')
        self.assertEqual(len(list_files_html), 6, "Not the same numbers of webcontent's files")
        print("[IMSArchiveTestCase]-- check_creation_webcontent OK --")

    def testNbWebActivite(self):
        """
        """
        list_files_ac = os.listdir(TEST_IMS_DIR+'/Activite')
        self.assertEqual(len(list_files_ac), 3, "Not the same numbers of Activite's files")
        print("[IMSArchiveTestCase]-- check_creation_Activite OK --")

    def testNbWebComprehension(self):
        """
        """
        list_files_com = os.listdir(TEST_IMS_DIR+'/Comprehension')
        self.assertEqual(len(list_files_com), 4, "Not the same numbers of Comprehension's files")
        print("[IMSArchiveTestCase]-- check_creation_Comprehension OK --")

    def testNbWebActiviteAvancee(self):
        """
        """
        list_files_acav = os.listdir(TEST_IMS_DIR+'/ActiviteAvancee')
        self.assertEqual(len(list_files_acav), 2, "Not the same numbers of ActiviteAvancee's files")
        print("[IMSArchiveTestCase]-- check_creation_ActiviteAvancee OK --")

    def testArchitectureManifest(self):
        """
        """
        tree = etree.parse(TEST_IMS_DIR+'/imsmanifest.xml')
        root = tree.getroot()
        self.assertTrue('manifest' in root.tag,'Not manifest root tag')
        for i,child in enumerate(root) :
            if i == 0 :
                self.assertTrue('metadata' in child.tag,'Not metadata tag')
                self.assertTrue('schema' in child[0].tag,'Not schema tag')
                self.assertTrue('IMS Common Cartridge' in child[0].text, 'Bad text for schema tag')
                self.assertTrue('schemaversion' in child[1].tag)
                self.assertTrue('1.1.0' in child[1].text)
                #lomimscc:lom
                self.assertTrue('lom' in child[2].tag)
                self.assertTrue('general' in child[2][0].tag)
                self.assertTrue('title' in child[2][0][0].tag)
                self.assertTrue('string' in child[2][0][0][0].tag)
                # self.assertTrue('fr' in child[2][0][0][0].attrib.get('language'))
            # FIXME : à finir
        print("[IMSArchiveTestCase]-- check_architecture_imsmanifest OK --")

    def testCreationQuizzIMS(self):
        """
        """
        io_ourQuestions = StringIO("""
::MULTIANSWER::
What two people are entombed in Grant's tomb? {
~%-100%No one
~%50%Grant #One comment
~%50%Grant's wife
~%-100%Grant's father
}

::TRUEFALSE1::
Vrai ou Faux?
{T #Non...#Exact !
####MEGA COMMENT
}

::TRUEFALSE2::
Faux ou Vrai?
{F #Pas bon...#C'est ça!
}

::SINGLEANSWER::
Question {
=A correct answer
~Wrong answer1
#A response to wrong
~Wrong answer2
#A response to wrong
~Wrong answer3
#A response to wrong
~Wrong answer4
#A response to wrong
}

::ESSAY::
Blablablabla {
#### MEGA COMMENT
}
        """)

        questions = pygift.parseFile(io_ourQuestions)
        #QUESTIONS
        multi = questions[0]
        trfl = questions[1]
        trfl2 = questions[2]
        sglans = questions[3]
        essay = questions[4]

        ims = toIMS.create_ims_test(questions,'1','multi')
        # print(ims)

        #TRANSFORM TO IMS
        imsmulti = toIMS.create_ims_test([multi],'1','multi')
        imstrfl = toIMS.create_ims_test([trfl],'2','trfl')
        imstrfl2 = toIMS.create_ims_test([trfl2],'3','trfl2')
        imssglans = toIMS.create_ims_test([sglans],'4','sglans')
        imsessay = toIMS.create_ims_test([essay],'5','essay')

        #MULTI
        self.assertTrue('<?xml version="1.0" encoding="UTF-8"?>'.strip() in imsmulti.strip())
        self.assertTrue("""<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_qtiasiv1p2p1_v1p0.xsd">""".strip() in imsmulti.strip())
        self.assertTrue("""<qtimetadata>
      <qtimetadatafield>
        <fieldlabel>qmd_scoretype</fieldlabel>
        <fieldentry>Percentage</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>qmd_hintspermitted</fieldlabel>
        <fieldentry>Yes</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>qmd_feedbackpermitted</fieldlabel>
        <fieldentry>Yes</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>cc_profile</fieldlabel>
        <fieldentry>cc.exam.v0p1</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>cc_maxattempts</fieldlabel>
        <fieldentry>1</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>qmd_assessmenttype</fieldlabel>
        <fieldentry>Examination</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>qmd_solutionspermitted</fieldlabel>
        <fieldentry>Yes</fieldentry>
      </qtimetadatafield>
    </qtimetadata>""".strip() in imsmulti.strip())
        self.assertTrue("""<rubric>
      <material label="Summary">
        <mattext texttype="text/html"></mattext>
      </material>
    </rubric>""".strip() in imsmulti.strip())
        self.assertTrue("""<section ident="section_1_test_1">
      <item ident="q_0" title="MULTIANSWER">""".strip() in imsmulti.strip())
        self.assertTrue("""<itemmetadata>
          <qtimetadata>
            <qtimetadatafield>
              <fieldlabel>cc_profile</fieldlabel>
              <fieldentry>cc.multiple_response.v0p1</fieldentry>
            </qtimetadatafield>
            <qtimetadatafield>
              <fieldlabel>cc_question_category</fieldlabel>
              <fieldentry>Quiz Bank multi</fieldentry>
            </qtimetadatafield>
          </qtimetadata>
        </itemmetadata>""".strip() in imsmulti.strip())
        self.assertTrue("""<presentation>
          <material>
            <mattext texttype="text/html">&lt;p&gt; What two people are entombed in Grant's tomb?&lt;/p&gt;</mattext>
          </material>""".strip() in imsmulti.strip())
        self.assertTrue("""<material>
                  <mattext texttype="text/html">&lt;p&gt;No one&lt;/p&gt;</mattext>
                </material>""".strip() in imsmulti.strip())
        self.assertTrue("""<material>
                  <mattext texttype="text/html">&lt;p&gt;Grant&lt;/p&gt;</mattext>
                </material>""".strip() in imsmulti.strip())
        self.assertTrue("""<material>
                  <mattext texttype="text/html">&lt;p&gt;Grant's wife&lt;/p&gt;</mattext>
                </material>""".strip() in imsmulti.strip())
        self.assertTrue("""<material>
                  <mattext texttype="text/html">&lt;p&gt;Grant's father&lt;/p&gt;</mattext>
                </material>
              </response_label>
            </render_choice>
          </response_lid>
        </presentation>""".strip() in imsmulti.strip())
        
# Main
if __name__ == '__main__':
    setUp()
    unittest.main(verbosity=1)
