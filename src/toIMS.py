#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals    # at top of module

import json
import logging
import os
import sys
import zipfile
import random
from io import open

from lxml import etree
from lxml import html
from markdown import markdown
from pprint import pprint
from yattag import indent
from yattag import Doc

import model
import utils

# utf8 hack, python 2 only !!
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')

######
##   reférences :
#       - http://www.imsglobal.org/cc/ccv1p2/imscc_profilev1p2-Implementation.html
#       - http://www.imsglobal.org/question/qtiv1p2/imsqti_asi_bindv1p2.html
#############

# Mapping of the types used in culturenumerique with IMSCC types
FILETYPES = {
    'weblink' : 'imswl_xmlv1p1',
    'discussions' : 'imsdt_xmlv1p1',
    'auto-evaluation' : 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
    'devoirs': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
    'Activite': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
    'ActiviteAvancee': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
    'Comprehension': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
    'webcontent' : 'webcontent',
    'correction' : 'webcontent',
    'cours' : 'webcontent',
}

# media folder is no longer copied along since all media are linked absolutely
FOLDERS = ['Activite', 'ActiviteAvancee', 'Comprehension', 'webcontent']

FOLDERS_ACTIVITY = {
    'Activite':'act',
    'ActiviteAvancee':'actav',
    'Comprehension':'test',
    'webcontent':'',
}

CC_PROFILES = {
    'MULTICHOICE' : 'cc.multiple_choice.v0p1',
    'MULTIANSWER' : 'cc.multiple_response.v0p1',
    'TRUEFALSE' : 'cc.multiple_choice.v0p1', #FIXME : doing that because of a bug in Moodle 3 that can no longer import TRUTRUEFALSE cc.true_false.v0p1
    'ESSAY' : 'cc.essay.v0p1',
    'DESCRIPTION': 'cc.essay.v0p1',
    'MISSINGWORD' : 'cc.fib.v0p1',
    'MATCH' : 'cc.pattern_match.v0p1'
}

IMS_HEADER = """<?xml version="1.0" encoding="UTF-8"?><manifest xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1"
    xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" identifier="M_3E1AEC6D" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd">
    """

HEADER_TEST = """<?xml version="1.0" encoding="UTF-8"?>
    <questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_qtiasiv1p2p1_v1p0.xsd">
    """

DEFAULT_QTI_META = {
    'cc_profile' : 'cc.exam.v0p1',
    'qmd_assessmenttype' : 'Examination',
    'qmd_scoretype':'Percentage',
    'qmd_feedbackpermitted':'Yes',
    'qmd_hintspermitted':'Yes',
    'qmd_solutionspermitted':'Yes',
    'cc_maxattempts':'unlimited'
}

def set_qti_metadata(max_attempts):

    meta, tag, text = Doc().tagtext()
    meta.asis("<!--  Metadata  -->")
    metadata = DEFAULT_QTI_META
    metadata['cc_maxattempts'] = max_attempts
    with tag('qtimetadata'):
        for key, value in metadata.iteritems():
            with tag('qtimetadatafield'):
                with tag('fieldlabel'):
                    text(key)
                with tag('fieldentry'):
                    text(value)

    return indent(meta.getvalue())

def create_ims_test(questions, test_id, test_title):
    """
    Supported types : ESSAY, MULTICHOICE, MULTIANSWER, TRUEFALSE, DESCRIPTION

    """
    # create magic yattag triple
    doc, tag, text = Doc().tagtext()
    doc.asis(HEADER_TEST+'\n')
    if 'ESSAY' in questions[0].type:
        max_attempts = 'unlimited'
    else:
        max_attempts = 1
    with tag('assessment', ident=test_id, title=test_title):
        doc.asis(set_qti_metadata(max_attempts))
        #<!-- Titre de l'execercice  -->
        with tag('rubric'):
            with tag('material', label="Summary"):
                with tag('mattext', texttype="text/html"):
                    text()
        # only one section in a test
        with tag('section', ident='section_1_test_'+test_id):
        # loop on questions
            for idx, question in enumerate(questions):
                with tag('item', ident='q_'+str(idx), title=question.title):
                    #<!--  metatata  -->
                    with tag('itemmetadata'):
                        with tag('qtimetadata'):
                            with tag('qtimetadatafield'):
                                with tag('fieldlabel'):
                                    text("cc_profile")
                                with tag('fieldentry'):
                                    try:
                                        text(CC_PROFILES[question.type])
                                    except:
                                        # default to essay
                                        text(CC_PROFILES['ESSAY'])
                            with tag('qtimetadatafield'):
                                with tag('fieldlabel'):
                                    text("cc_question_category")
                                with tag('fieldentry'):
                                    text('Quiz Bank '+test_title)
                    #Contenu de la question
                    with tag('presentation'):
                        # Enoncé
                        with tag('material'):
                            with tag('mattext', texttype='text/html'):
                                text(question.text )
                        # réponses possibles
                        if 'ESSAY' in question.type:
                            with tag('response_str', rcardinality='Single', ident='response_'+str(question.id)):
                                doc.stag('render_fib', rows=5, prompt='Box', fibtype="String")
                        elif question.type in (('MULTICHOICE', 'MULTIANSWER', 'TRUEFALSE')):
                            if question.type == 'MULTIANSWER':
                                rcardinality = 'Multiple'
                            else:
                                rcardinality = 'Single'
                            # rcardinality optional, but a priori 'Single' form MChoice, 'Multiple' for Manswer;
                            with tag('response_lid', rcardinality=rcardinality, ident='response_'+str(question.id)):
                                with tag('render_choice', shuffle='No'):
                                    for id_a, answer in enumerate(question.answers):
                                        with tag('response_label', ident='answer_'+str(question.id)+'_'+str(id_a)):
                                            with tag('material'):
                                                with tag('mattext', texttype="text/html"):
                                                    text(answer['answer_text'])
                        else: # FIXME add support for NUMERIC, MATCHING, etc
                            pass
                    # Response Processing
                    with tag('resprocessing'):
                        # outcomes: FIXME: allways the same ?
                        with tag('outcomes'):
                            doc.stag('decvar', varname='SCORE', vartype='Decimal', minvalue="0", maxvalue="100")
                        # respconditions pour décrire quelle est la bonne réponse, les interactions, etc
                        if question.global_feedback != '':
                            with tag('respcondition', title='General feedback', kontinue='Yes'):
                                with tag('conditionvar'):
                                    doc.stag('other')
                                doc.stag('displayfeedback', feedbacktype="Response", linkrefid='general_fb')
                        ## lister les autres interactions/conditions
                        if question.type in (('MULTICHOICE','TRUEFALSE')):
                            for id_a, answer in enumerate(question.answers):
                                score = 0
                                if answer['is_right']:
                                    title = 'Correct'
                                    score = 100
                                else:
                                    title = ''
                                    score = answer['credit']
                                with tag('respcondition', title=title):
                                    with tag('conditionvar'):
                                        with tag('varequal', respident='response_'+str(question.id)): # respoident is id of response_lid element
                                            text('answer_'+str(question.id)+'_'+str(id_a))
                                    with tag('setvar', varname='SCORE', action='Set'):
                                        text(score)
                                    doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_'+str(id_a))
                        elif question.type == 'MULTIANSWER':
                            # Correct combination
                            with tag('respcondition', title="Correct", kontinue='No'):
                                with tag('conditionvar'):
                                    with tag('and'):
                                        for id_a, answer in enumerate(question.answers):
                                            score = 0
                                            try:
                                                score = float(answer['credit'])
                                            except:
                                                pass
                                            if score <= 0:
                                                with tag('not'):
                                                    with tag('varequal', case='Yes', respident='response_'+str(question.id)): # respoident is id of response_lid element
                                                        text('answer_'+str(question.id)+'_'+str(id_a))
                                            else:
                                                with tag('varequal', case='Yes', respident='response_'+str(question.id)): # respoident is id of response_lid element
                                                    text('answer_'+str(question.id)+'_'+str(id_a))
                                with tag('setvar', varname='SCORE', action='Set'):
                                    text('100')
                                doc.stag('displayfeedback', feedbacktype='Response', linkrefid='general_fb')
                            # default processing in any case
                            for id_a, answer in enumerate(question.answers):
                                with tag('respcondition', kontinue='No'):
                                    with tag('conditionvar'):
                                        with tag('varequal', respident='response_'+str(question.id), case="Yes"):
                                            text('answer_'+str(question.id)+'_'+str(id_a))
                                    doc.stag('displayfeedback', feedbacktype='Response', linkrefid='feedb_'+str(id_a))
                        else:
                            pass
                    # liste les feedbacks
                    ## feedback general
                    if question.global_feedback != '':
                        with tag('itemfeedback', ident='general_fb'):
                            with tag('flow_mat'):
                                with tag('material'):
                                    with tag('mattext', texttype='text/html'):
                                        text(question.global_feedback)
                    ## autres feedbacks
                    for id_a, answer in enumerate(question.answers):
                        with tag('itemfeedback', ident='feedb_'+str(id_a)):
                            with tag('flow_mat'):
                                with tag('material'):
                                    with tag('mattext', texttype='text/html'):
                                        text(answer['feedback'])
                    ## FIXME add wrong and correct feedbacks for TRUEFALSE
    doc.asis('</questestinterop>\n')
    doc_value = indent(doc.getvalue().replace('\n', '')) #pre-escaping new lines because of a bug in moodle that turn them in <br>
    doc_value = doc_value.replace('kontinue', 'continue')
    return doc_value

def create_empty_ims_test(id, num, title, max_attempts):
    """
        create empty imsc test source code
    """
    src = HEADER_TEST
    src += '<assessment ident="'+id+'" title="'+num+' '+title+'">\n'
    src += set_qti_metadata(max_attempts)
    src += "</assessment></questestinterop>\n"

    return src


def generateIMSManifest(m):
    """ parse m from config file 'moduleX.config.json' and recreate imsmanifest.xml """
    # create magic yattag triple
    doc, tag, text = Doc().tagtext()
    # open tag 'manifest' with default content:
    doc.asis(IMS_HEADER)
    # Print metam
    with tag('metadata'):
        with tag('schema'):
            text('IMS Common Cartridge')
        with tag('schemaversion'):
            text('1.1.0')
        with tag('lomimscc:lom'):
            with tag('lomimscc:general'):
                with tag('lomimscc:title'):
                    with tag('lomimscc:string', language=m.language):
                        text(m.menutitle)
                with tag('lomimscc:language'):
                    text(m.language)
                with tag('lomimscc:description'):
                    doc.stag('lomimscc:string', language=m.language)
                with tag('lomimscc:identifier'):
                    with tag('lomimscc:catalog'):
                        text('category')
                    with tag('lomimscc:entry'):
                        try:
                            text(m.category)
                        except:
                            text('D')
    # Print organization
    resources = []
    with tag('organizations'):
        with tag('organization', identifier="organization0", structure='rooted-hierarchy'):
            with tag('item', identifier='root'):
                # add empty section as section "0 . Généralités" to avoid wrong numbering
                with tag('item', identifier='section_generalites'):
                    with tag('title'):
                        # doc.asis('<![Cm[<span class="ban-sec ban-howto"></span>]]>')
                        doc.asis('')
                for idA, section in enumerate(m.sections):
                    section_id = "sec_"+(str(idA))
                    with tag('item', identifier=section_id):
                        with tag('title'):
                            doc.asis('<![CDATA[<span class="sumtitle">'+section.num+' '+section.title+'</span>]]>')
                        subsec_type_old = ''
                        subsec_type = ''
                        for idB, subsection in enumerate(section.subsections):
                            subsec_type_old = subsec_type
                            subsec_type = subsection.folder
                            href = subsection.folder+'/'+subsection.filename
                            # when adding moodle-test type change file suffix from .html.xml
                            if subsec_type in ['Activite', 'ActiviteAvancee', 'Comprehension']:
                                href = href.replace('html', 'xml')
                            filename = href.rsplit('/',1)[1]
                            resources.append(filename)
                            with tag('item', identifier=("subsec_"+str(idA)+"_"+str(idB)), identifierref=("doc_"+str(idA)+"_"+str(idB))):
                                with tag('title'):
                                    if subsec_type == 'webcontent':
                                        text(subsection.num+' '+subsection.title)
                                    else:
                                        # subsec_type != 'webcontent':
                                        if subsec_type != subsec_type_old:
                                            doc.asis('<![CDATA[<span class="ban-sub ban-'+FOLDERS_ACTIVITY[subsec_type]+'">'+subsection.num+' '+subsection.title+'</span>]]>')
                                        else:
                                            text(subsection.num+' '+subsection.title)

    # Print resources
    with tag('resources'):
        doc.asis("<!-- Webcontent -->")
        for idA, section in enumerate(m.sections):
            for idB, subsection in enumerate(section.subsections):
                doc_id = "doc_"+str(idA)+"_"+str(idB)
                file_type = FILETYPES[subsection.folder]
                # When adding moodle test resource change file suffix from .html to .xml
                href = subsection.folder+'/'+subsection.filename
                if subsection.folder in ['Activite', 'ActiviteAvancee', 'Comprehension']:
                    href = href.replace('html', 'xml')
                with tag('resource', identifier=doc_id, type=file_type, href=href):
                     doc.stag('file', href=href)

    doc.asis("</manifest>") # IMS footer
    return indent(doc.getvalue())

def generateImsArchive(module_object, module_name, module_directory):
    # Prepare paths and directories
    cur_dir = os.getcwd()
    os.chdir(module_directory)
    ims_outdir = os.path.join(module_directory, 'IMS')
    os.makedirs(ims_outdir)
    utils.createDirs(ims_outdir, FOLDERS)

    # Generate Html and XML files
    for section in module_object.sections:
        for sub in section.subsections:
            if sub.folder == 'webcontent':
                utils.write_file(sub.html_src, ims_outdir, sub.folder, sub.getFilename())
            else:
                utils.write_file(sub.toXMLMoodle(), ims_outdir, sub.folder, sub.getFilename('xml'))

    # parse data and generate imsmanifest.xml
    imsfilename = os.path.join(ims_outdir, 'imsmanifest.xml')
    imsfile = open(imsfilename, 'w', encoding='utf-8')
    imsfile.write(generateIMSManifest(module_object))
    imsfile.close()
    logging.warning("[toIMS] imsmanifest.xml saved for module %s", module_directory)

    # Compress relevant files
    fileout = module_name+'.imscc.zip'
    zipf = zipfile.ZipFile(fileout, 'w')
    zipf.write(imsfilename)
    for dir_name in FOLDERS:
        try:
            if os.listdir(os.path.join(ims_outdir, dir_name)):
                for afile in os.listdir(os.path.join(ims_outdir, dir_name)):
                    filepath = os.path.join(ims_outdir, dir_name, afile)
                    logging.info("[toIMS] Adding %s to archive " % (filepath))
                    zipf.write(filepath)
        except:
            continue

    zipf.close()
    os.chdir(cur_dir)
    return fileout

def main(argv):
    """
    """
    import argparse
    parser = argparse.ArgumentParser(description="toIMS is a utility to help building imscc archives for exporting curent material to Moodle. Usage: $ python toIMS.py -d module_directory -n module_name .")
    parser.add_argument("-d", "--module_directory", help="Set the module directory", default='.')
    parser.add_argument("-n", "--module_name", help="Set the name of the module", default='module')

    args = parser.parse_args()

    fileout_path = generateImsArchive(args.module_name, args.module_directory)
    print("archive generated %s" % fileout_path)
    exit(0)


############### main ################
if __name__ == "__main__":
    main(sys.argv)
