 #!/usr/bin/python3
# -*- coding: utf-8 -*-

from io import open
import json
import mock
from pygiftparser import parser as pygift

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

from src import model, toEDX

TEST_EDX_DIR = "./testEDX"


def setUp():
    """
    Build EDX folder based on coursTest
    """
    with open("coursTest/module1/module_test.md", encoding='utf-8') as sample_file:
        global m
        m = model.Module(sample_file, "tests", "http://culturenumerique.univ-lille3.fr")
        m.toHTML()
        m_json = json.loads(m.toJson(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        if os.path.isdir(TEST_EDX_DIR):
            shutil.rmtree(TEST_EDX_DIR)
        m.edx_archive_path = toEDX.generateEDXArchive(m, TEST_EDX_DIR)
        sample_file.close()
        del m_json,sample_file

class EDXArchiveTestCase(unittest.TestCase):


    def testCreationDossierEdx(self):
        """
        Check if all directories and files are created
        """
        self.assertTrue(os.path.isdir(TEST_EDX_DIR),"dir "+TEST_EDX_DIR+" don't exist")
        self.assertTrue(os.path.exists(TEST_EDX_DIR+'/tests_edx.tar.gz'), "tar.gz don't exist")
        self.assertTrue(os.path.isdir(TEST_EDX_DIR+'/EDX'), "dir EDX don't exist")
        self.assertTrue(os.path.exists(TEST_EDX_DIR+'/EDX/course.xml'), "file course.xml don't exist")
        self.assertTrue(os.path.exists(TEST_EDX_DIR+'/EDX/about/overview.html'), "file overview.html don't exist")
        self.assertTrue(os.path.exists(TEST_EDX_DIR+'/EDX/assets/assets.xml'), "file assets.xml don't exist")
        self.assertTrue(os.path.isdir(TEST_EDX_DIR+'/EDX/html'), "dir html don't exist")
        self.assertTrue(os.path.exists(TEST_EDX_DIR+'/EDX/info/updates.html'), "file updates.html don't exist")
        self.assertTrue(os.path.isdir(TEST_EDX_DIR+'/EDX/policies'), "dir policies don't exist")
        self.assertTrue(os.path.isdir(TEST_EDX_DIR+'/EDX/problem'), "dir problem don't exist")

        print("[EDXArchiveTestCase]-- check_creation_dossier_edx OK --")

    def testNbWebContent(self):
        """
        Check the correct number of WebContent's courses
        """
        list_files_html = os.listdir(TEST_EDX_DIR+'/EDX/html')
        self.assertEqual(len(list_files_html), 6, "Not the same numbers of HTML's files")
        print("[EDXArchiveTestCase]-- check_nb_web_content OK --")

    def testNbProblems(self):
        """
        Check the correct number of Activities
        """
        list_files_problems = os.listdir(TEST_EDX_DIR+'/EDX/problem')
        self.assertEqual(len(list_files_problems), 20, "Not the same numbers of Problem's files")

        print("[EDXArchiveTestCase]-- check_nb_problems OK --")

    def testCntCours(self):
        """
        Check the file course.xml
        """
        cpt_act = 0
        cpt_comp = 0
        cpt_act_av = 0
        #transform xml files in XLM object Python
        tree = etree.parse(TEST_EDX_DIR+'/EDX/course.xml')
        #Collect all sequential tag in tree & test existence
        list_seq = tree.xpath("/course/chapter/sequential")
        self.assertNotEquals(list_seq, [])
        for i,vert in enumerate(list_seq):
            # Check if sequential have only one vertical tag
            self.assertEquals(len(vert),1,"Lenght vertical n°"+str(i)+" > 1")
            fm = vert.attrib.get("format")
            if fm == "Activite":
                cpt_act += 1
            elif fm == "Activite Avancee":
                cpt_act_av += 1
            elif fm == "Comprehension":
                cpt_comp += 1
        #Collect all chapter tag in tree
        list_chap = tree.xpath("/course/chapter")
        self.assertNotEquals(list_chap, [])
        #Collect all problem tag in tree
        list_pro = tree.xpath("/course/chapter/sequential/vertical/problem")
        self.assertNotEquals(list_pro, [])
        #Collect all html tag in tree
        list_html = tree.xpath("/course/chapter/sequential/vertical/html")
        self.assertNotEquals(list_html, [])


        #ASSERTS XML TREE
        self.assertEquals(len(list_pro),20,"Not the same nb of problems")
        self.assertEquals(len(list_chap),4,"Not the same nb of chapters")
        self.assertEquals(len(list_seq),15,"Not the same nb of sequentials")
        self.assertEquals(len(list_html),6,"Not the same nb of webcontent")

        #ASSERTS CNT
        self.assertEquals(cpt_act,3,"Not the same nb of Activite")
        self.assertEquals(cpt_act_av,2,"Not the same nb of ActiviteAvancee")
        self.assertEquals(cpt_comp,4,"Not the same nb of Comprehension")

        print("[EDXArchiveTestCase]-- check_nb_cnt_cours OK --")

    def testCNVideo(self):
        """
        Test if video is correctly formating and insert into course.xml
        """
        tree = etree.parse(TEST_EDX_DIR+'/EDX/course.xml')
        root = tree.getroot()
        l_video = root.iter('cnvideo')
        vid = l_video.next()
        self.assertEquals(vid.attrib.get('url_name'),'1-1-1-https-vimeo-com-122104210')
        vid = l_video.next()
        self.assertEquals(vid.attrib.get('url_name'),'1-3-1-https-vimeo-com-122104443')
        vid = l_video.next()
        self.assertEquals(vid.attrib.get('url_name'),'2-3-1-https-vimeo-com-122104499')
        vid = l_video.next()
        self.assertEquals(vid.attrib.get('url_name'),'1-4-1-https-vimeo-com-122104174')

        print("[EDXArchiveTestCase]-- check_CNVideo OK --")

    def testProblem(self):
        io_ourQuestions = StringIO("""
::MULTIANSWER::
What two people are entombed in Grant's tomb? {
~%-100%No one
~%50%Grant #One comment
~%50%Grant's wife
~%-100%Grant's father
}

::TRUEFALSE::
Vrai ou Faux?
{T #Non...#Exact !
####MEGA COMMENT
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
        sglans = questions[2]
        essay = questions[3]

        #MULTIANSWER
        rootm = etree.fromstring(multi.toEDX())
        self.assertEqual(rootm.tag,"problem", "for MULTIANSWER, problem tag was not created")
        self.assertEqual(rootm.attrib.get("display_name"),"MULTIANSWER","for MULTIANSWER, title was not assigned")
        self.assertEqual(rootm.attrib.get("max_attempts"),"1","for MULTIANSWER, max_attempts was not assigned")
        for i,child in enumerate(rootm):
            if i == 0:
                self.assertEqual(child.tag,"legend", "for MULTIANSWER, legend tag was not created")
            if i == 1:
                self.assertEqual(child.tag,"choiceresponse", "for MULTIANSWER, choiceresponse tag was not created")
                self.assertEqual(child.attrib.get("partial_credit"), "EDC")
                checkbox = child[0]
                self.assertEqual(checkbox.tag,"checkboxgroup")
                for j,greatChild in enumerate(checkbox):
                    self.assertEqual(greatChild.tag,"choice")
                    self.assertNotEqual(j,4,"for MULTIANSWER, More than 4 elements")
                    if j == 0:
                        self.assertEqual(greatChild.text,"No one")
                    if j == 1:
                        self.assertEqual(greatChild.text,"Grant")
                        self.assertEqual(greatChild[0].tag,"choicehint")
                        self.assertEqual(greatChild[0].attrib.get("selected"),"true")
                        self.assertEqual(greatChild[0].text,"Grant : One comment")
                    if j == 2:
                        self.assertEqual(greatChild.text,"Grant's wife")
                    if j == 3:
                        self.assertEqual(greatChild.text,"Grant's father")
            if i == 2:
                self.assertEqual(child.tag,"solution")
                self.assertEqual(child[0].attrib.get("class"),"detailed-solution")

        #TRUEFALSE
        roottf = etree.fromstring(trfl.toEDX())
        self.assertEqual(roottf.tag,"problem", "for TRUEFALSE, problem tag was not created")
        self.assertEqual(roottf.attrib.get("display_name"),"TRUEFALSE","for TRUEFALSE, title was not assigned")
        self.assertEqual(roottf.attrib.get("max_attempts"),"1","for TRUEFALSE, max_attempts was not assigned")
        for i,child in enumerate(roottf):
            if i == 0:
                self.assertEqual(child.tag,"legend", "for TRUEFALSE, legend tag was not created")
            if i == 1:
                self.assertEqual(child.tag,"multiplechoiceresponse", "for TRUEFALSE, multiplechoiceresponse tag was not created")
                choicegroup = child[0]
                self.assertEqual(choicegroup.tag,"choicegroup")
                #TRUE
                self.assertEqual(choicegroup[0].tag,"choice")
                self.assertEqual(choicegroup[0].text,"Vrai")
                self.assertEqual(choicegroup[0].attrib.get("correct"),"true")
                self.assertEqual(choicegroup[0][0].tag,"choicehint")
                self.assertEqual(choicegroup[0][0].text,"Exact !")
                #FALSE
                self.assertEqual(choicegroup[1].tag,"choice")
                self.assertEqual(choicegroup[1].text,"Faux")
                self.assertEqual(choicegroup[1].attrib.get("correct"),"false")
                self.assertEqual(choicegroup[1][0].tag,"choicehint")
                self.assertEqual(choicegroup[1][0].text,"Non...")
            if i == 2:
                self.assertEqual(child.tag,"solution")
                self.assertEqual(child[0].attrib.get("class"),"detailed-solution")
                self.assertEqual(child[0][0].text,"MEGA COMMENT")

        #SINGLEANSWER
        roots = etree.fromstring(sglans.toEDX())
        self.assertEqual(roots.tag,"problem", "for SINGLEANSWER, problem tag was not created")
        self.assertEqual(roots.attrib.get("display_name"),"SINGLEANSWER","for TRUEFALSE, title was not assigned")
        self.assertEqual(roots.attrib.get("max_attempts"),"1","for SINGLEANSWER, max_attempts was not assigned")
        for i,child in enumerate(roots):
            if i == 0:
                self.assertEqual(child.tag,"legend", "for SINGLEANSWER, legend tag was not created")
            if i == 1:
                self.assertEqual(child.tag,"multiplechoiceresponse", "for SINGLEANSWER, multiplechoiceresponse tag was not created")
                choicegroup = child[0]
                self.assertEqual(choicegroup.tag,"choicegroup")
                for j,greatChild in enumerate(choicegroup):
                    self.assertEqual(greatChild.tag,"choice")
                    self.assertNotEqual(j,5,"for SINGLEANSWER, More than 4 elements")
                    if j == 0:
                        self.assertEqual(greatChild.text,"A correct answer")
                        self.assertEqual(greatChild.attrib.get("correct"),"true")
                    if j == 1:
                        self.assertEqual(greatChild.text,("Wrong answer1"))
                        self.assertEqual(greatChild.attrib.get("correct"),"false")
                        self.assertEqual(greatChild[0].tag,("choicehint"))
                        self.assertEqual(greatChild[0].text,("A response to wrong"))
                    if j == 2:
                        self.assertEqual(greatChild.text,("Wrong answer2"))
                        self.assertEqual(greatChild.attrib.get("correct"),"false")
                        self.assertEqual(greatChild[0].tag,("choicehint"))
                        self.assertEqual(greatChild[0].text,("A response to wrong"))
                    if j == 3:
                        self.assertEqual(greatChild.text,("Wrong answer3"))
                        self.assertEqual(greatChild.attrib.get("correct"),"false")
                        self.assertEqual(greatChild[0].tag,("choicehint"))
                        self.assertEqual(greatChild[0].text,("A response to wrong"))
                    if j == 4:
                        self.assertEqual(greatChild.text,("Wrong answer4"))
                        self.assertEqual(greatChild.attrib.get("correct"),"false")
                        self.assertEqual(greatChild[0].tag,("choicehint"))
                        self.assertEqual(greatChild[0].text,("A response to wrong"))
                if i == 2:
                    self.assertEqual(child.tag,"solution")
                    self.assertEqual(child[0].attrib.get("class"),"detailed-solution")

        #ESSAY
        roote = etree.fromstring(essay.toEDX())
        self.assertEqual(roote.tag,"problem", "for ESSAY, problem tag was not created")
        self.assertEqual(roote.attrib.get("display_name"),"ESSAY","for ESSAY, title was not assigned")
        self.assertEqual(roote.attrib.get("max_attempts"),"1","for ESSAY, max_attempts was not assigned")
        for i,child in enumerate(roote):
            if i == 0:
                self.assertEqual(child.tag,"legend", "for ESSAY, legend tag was not created")
            if i == 1:
                self.assertEqual(child.tag,"script", "for ESSAY, frst script tag was not created")
                self.assertEqual(child.attrib.get("type"),"loncapa/python")
            if i == 2:
                self.assertEqual(child.tag,"span", "for ESSAY, span tag was not created")
                self.assertEqual(child.attrib.get("id"), str(essay.id))
            if i == 3:
                self.assertEqual(child.tag,"script", "for ESSAY, snd script tag was not created")
                self.assertEqual(child.attrib.get("type"),"text/javascript")
                self.assertTrue(child.text.find('<textarea style="height:150px" rows="20" cols="70"/>'))
            if i == 4:
                self.assertEqual(child.tag,"customresponse", "for ESSAY, customresponse tag was not created")
                self.assertEqual(child[0].tag,"textline", "for ESSAY, textline tag was not assigned")
            if i == 5:
                self.assertEqual(child.tag,"solution")
                self.assertEqual(child[0].attrib.get("class"),"detailed-solution")
                self.assertEqual(child[0][0].text,"MEGA COMMENT")


    def runTest(self):
        self.testCreationDossierEdx()
        self.testNbWebContent()
        self.testNbProblems()
        self.testCntCours()
        self.testCNVideo()
        self.testProblem()


# Main
if __name__ == '__main__':
    setUp()
    unittest.main(verbosity=1)
