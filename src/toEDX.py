#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
import logging
import shutil
import glob
import tarfile

from lxml import etree
from lxml import html
import markdown
from lxml.html.clean import Cleaner
from io import open
from jinja2 import Template, Environment, FileSystemLoader

import utils
import model


MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
BASE_PATH = os.path.abspath(os.getcwd())
EDX_TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates', 'toEDX' )
EDX_DEFAULT_FILES = {
    'about':'overview.html',
    'assets':'assets.xml',
    'info':'updates.html',
    'policies':'assets.json'
}
EDX_ADVANCED_MODULE_LIST = ['cnvideo', 'library_content']
EDX_GRADER_MAP = {
    'Activite':'Activite',
    'ActiviteAvancee':'Activite Avancee',
    'Comprehension':'Comprehension',
    'webcontent': None,
}

def generateEDXArchive(module, moduleOutDir):
    """ Given a module object and destination dir, generate EDX archive """

    jenv = Environment(loader=FileSystemLoader(EDX_TEMPLATES_PATH))
    jenv.filters['slugify'] = utils.cnslugify

    # Module data
    module.advanced_EDX_module_list = EDX_ADVANCED_MODULE_LIST.__str__()

    # create EDX archive temp folder
    edx_outdir = os.path.join(moduleOutDir, 'EDX')
    os.makedirs(edx_outdir)

    # generate content files: html/webcontent | problem/(Activite|ActiviteAvancee|Comprehension)
    for sec in module.sections:
        for sub in sec.subsections:
            if sub.folder == 'webcontent': # these go to EDX/html/
                utils.write_file(sub.html_src, edx_outdir, 'html', sub.filename )
            elif sub.folder in ('Activite', 'ActiviteAvancee', 'Comprehension'):
                for question in sub.questions:
                    fname =  ('%s.xml' % question.id)
                    fsrc = question.toEdxXML()
                    utils.write_file(fsrc, edx_outdir, 'problem', fname )

    # Add other files
    for folder, dfile in EDX_DEFAULT_FILES.items():
        shutil.copytree(os.path.join(EDX_TEMPLATES_PATH, folder), os.path.join(edx_outdir,folder))

    # Render and add policies/course files
    course_policies_files =  ['grading_policy.json', 'policy.json']
    for pfile in course_policies_files:
        pfile_template = jenv.get_template(os.path.join('policies','course', pfile))
        pjson = pfile_template.render(module=module)
        pjson = json.dumps(json.loads(pjson),ensure_ascii=True,indent=4,separators=(',', ': '))
        utils.write_file(pjson, os.getcwd(), os.path.join(edx_outdir, 'policies', 'course'), pfile)

    # Write main course.xml file
    course_template = jenv.get_template("course.tmpl.xml")
    course_xml = course_template.render(module=module, grademap=EDX_GRADER_MAP)
    utils.write_file(course_xml, os.getcwd(), edx_outdir, 'course.xml')

    # pack it up into a tar archive
    archive_file = os.path.join(moduleOutDir, ('%s_edx.tar.gz' % module.module))
    with tarfile.open(archive_file, "w:gz") as tar:
        for afile in os.listdir(edx_outdir):
            tar.add(os.path.join(edx_outdir, afile))
    tar.close()