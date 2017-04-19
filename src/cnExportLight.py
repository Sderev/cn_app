
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

import zipfile
from zipfile import ZipFile
import StringIO
from io import TextIOWrapper


MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates' )
LOGFILE = 'logs/cnExport.log'

#################
##    module   ##
#################

#module="moduleX"
def processModuleLight(moduleName, moduleData, repoDir, outDir, baseUrl):

    moduleDir=repoDir+'/'+moduleName

    f = moduleData
    text_f = TextIOWrapper(f.file, encoding='utf-8')

    m = model.Module(text_f, moduleName, baseUrl)
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

# Adding an entire folder to a zip file (used for the static folder)
def addFolderToZip(myZipFile,folder_src,folder_dst):
    folder_src = folder_src.encode('ascii') #convert path to ascii for ZipFile Method
    for file in glob.glob(folder_src+"/*"):
        if os.path.isfile(file):
            #print folder_dst+os.path.basename(file)
            myZipFile.write(file, folder_dst+os.path.basename(file), zipfile.ZIP_DEFLATED)
        elif os.path.isdir(file):
            addFolderToZip(myZipFile,file,folder_dst+os.path.basename(file)+'/')

def writeMediaFromArchive(zipFile, mediaData, path):

    #print mediaData.read()

    tarArchiveIO = StringIO.StringIO()
    tarArchiveIO.write(mediaData.read())
    tarArchiveIO.seek(0)

    # We open the tar archive inside of the StringIO instance
    with tarfile.open(mode='r:gz', fileobj=tarArchiveIO) as tar:
        for member in tar.getnames():
            zipFile.writestr(path+'/'+member, tar.extractfile(member).read())
        tar.close()

    return zipFile

#Construction du site
#retourne l'archive
def buildSiteLight(course_obj, repoDir, outDir, mediasData ,homeData, titleData, logoData):

    #print BASE_PATH
    inMemoryOutputFile = StringIO.StringIO()
    zipFile = ZipFile(inMemoryOutputFile, 'w')
    addFolderToZip(zipFile,BASE_PATH+'/static/','static/')

    jenv = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    jenv.filters['slugify'] = utils.cnslugify
    site_template = jenv.get_template("site_layout.html")

    ####LOGO
    #if found, copy logo.png, else use default
    logo_files=logoData
    if len(logo_files.name) > 0:
        logo="logo.png"
        zipFile.writestr(logo, logo_files.read())
    else:# use default one set in template
        logo = 'default'

    ####TITLE
    course_obj.title=titleData

    ####INDEX
    custom_home = False
    try:
        f = homeData
        home_data = f.read()
        home_html = markdown.markdown(home_data, MARKDOWN_EXT)
        custom_home = True

    except Exception as err:
        ## use default from template
        logging.error(" Cannot parse home markdown ")
        with open(os.path.join(TEMPLATES_PATH, 'default_home.html'), 'r', encoding='utf-8') as f:
            home_html = f.read()

    ####INDEX
    ## write index.html file
    html = site_template.render(course=course_obj, module_content=home_html,body_class="home", logo=logo, custom_home=custom_home)
    zipFile.writestr('index.html', html.encode("UTF-8"))


    ####MODULE
    # Loop through modules
    for module,mediaData in zip(course_obj.modules,mediasData):
        zipFile = toEDX.generateEDXArchiveLight(module, module.module, zipFile)
        zipFile = toIMS.generateImsArchiveLight(module, module.module, zipFile)

        # write html, XML, and JSon files
        file_path=module.module

        if mediaData:
            zipFile=writeMediaFromArchive(zipFile,mediaData,file_path+'/media')

        zipFile.writestr(file_path+'/'+module.module+'.questions_bank.gift.txt', module.toGift().encode("UTF-8"))
        zipFile.writestr(file_path+'/'+module.module+'.video_iframe_list.txt', module.toVideoList().encode("UTF-8"))
        mod_config=zipFile.writestr(file_path+'/'+module.module+'.config.json', module.toJson().encode("UTF-8")) # FIXME : this file should be optionnaly written

        module_template = jenv.get_template("module.html")
        module_html_content = module_template.render(module=module)
        html = site_template.render(course=course_obj, module_content=module_html_content, body_class="modules", logo=logo)
        zipFile.writestr(module.module+'.html', html.encode("UTF-8"))

    zipFile.close()
    inMemoryOutputFile.seek(0)

    return inMemoryOutputFile

def generateArchive(modulesData, mediasData, homeData, titleData, logoData, repoDir, outDir, baseUrl):
    modules=[]
    i=1
    for moduleData in modulesData:
        m=processModuleLight("module"+str(i),moduleData,repoDir,outDir,baseUrl)
        modules.append(m)
        i=i+1
    c=processRepositoryLight(modules,repoDir,outDir)

    #mediasDataObj=extractArchive(mediasData)
    outputFile=buildSiteLight(c,repoDir,outDir,mediasData,homeData,titleData, logoData)

    return outputFile

"""
def extractArchive(mediasData):
    mediasDataObj=[]

    for mediaData in mediasData:
        #print mediaData.read()
        tarArchiveIO = StringIO.StringIO()
        tarArchiveIO.write(mediasData.read())
        tarArchiveIO.seek(0)

        # We open the tar archive inside of the StringIO instance
        with tarfile.open(mode='r:gz', fileobj=tarArchiveIO) as tar:
            for member in tar.getnames():
                media=StringIO.StringIO()
                media.write(tar.extractfile(member).read())
                mediasDataObj.append(media)
            tar.close()
        return mediasDataObj
"""
