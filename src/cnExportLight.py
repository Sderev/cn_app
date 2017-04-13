
#!cnappenv/bin/python
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
from yattag import indent
from yattag import Doc
from lxml.html.clean import Cleaner
from io import open
from jinja2 import Template, Environment, FileSystemLoader

import utils
import toIMS
import toEDX
import model
from zipCreator import ZipStreamer

MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates' )
LOGFILE = 'logs/cnExport.log'

#################
##    module   ##
#################

#module="moduleX"
def processModuleLight(moduleName, moduleData, repoDir, outDir, baseUrl,):
    moduleDir = os.path.join(repoDir, moduleName)


    #filein = utils.fetchMarkdownFile(moduleDir)
    #with open(form.cleaned_data["home"], encoding='utf-8') as md_file:
    m = model.Module(moduleData, moduleName, baseUrl)
    m.toHTML(True) # only generate html for all subsections

    return m


#####################
##    course_obj   ##
#####################
def processRepositoryLight(modules, repoDir, outDir):
    #creation course_obj
    course_obj = model.CourseProgram(repoDir)

    for module in modules:
        course_obj.modules.append(module)
    return course_obj



#Construction du site
def buildSiteLight(course_obj, repoDir, outDir,homeData):

    logo = 'default'

    jenv = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    jenv.filters['slugify'] = utils.cnslugify
    site_template = jenv.get_template("site_layout.html")


    custom_home = False
    try:
        f = homeData
        #home_file = os.path.join(repoDir, 'home.md')
        #with open(home_file, 'r', encoding='utf-8') as f:
        home_data = f.read()
        home_html = markdown.markdown(home_data, MARKDOWN_EXT)
        custom_home = True

    except Exception as err:
        ## use default from template
        logging.error(" Cannot parse home markdown ")
        with open(os.path.join(TEMPLATES_PATH, 'default_home.html'), 'r', encoding='utf-8') as f:
            home_html = f.read()

    ### generation index

    ## write index.html file
    html = site_template.render(course=course_obj, module_content=home_html,body_class="home", logo=logo, custom_home=custom_home)
    #utils.write_file(html, os.getcwd(), outDir, 'index.html')

    ### generation module
    # Loop through modules
    for module in course_obj.modules:
        module_template = jenv.get_template("module.html")
        module_html_content = module_template.render(module=module)
        html = site_template.render(course=course_obj, module_content=module_html_content, body_class="modules", logo=logo)
        #utils.write_file(html, os.getcwd(), outDir, module.module+'.html')
    return html

def generateArchive(modulesData, homeData, repoDir, outDir, baseUrl):
    modules=[]
    for moduleData in modulesData:
        m=processModuleLight("module1",moduleData,repoDir,outDir,baseUrl,)
        modules.append(m)
    c=processRepositoryLight(modules,repoDir,outDir)
    html=buildSiteLight(c,repoDir,outDir,homeData)

    zip=ZipStreamer()
    zip.put_file("test")
    zip.write(html)

    return zip
