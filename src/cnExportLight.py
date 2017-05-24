
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
import re

MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates' )
LOGFILE = 'logs/cnExport.log'

#################
##    module   ##
#################

#module="moduleX"
def processModuleLight(moduleName, moduleData):

    #moduleDir=repoDir+'/'+moduleName

    m = model.Module(moduleData, moduleName, '')
    m.toHTML(True) # only generate html for all subsections

    return m


#####################
##    course_obj   ##
#####################
def processRepositoryLight(modules):
    #creation course_obj
    course_obj = model.CourseProgram('')

    for module in modules:
        course_obj.modules.append(module)
    return course_obj

# Adding an entire folder to a zip file (used for the static folder)
def addFolderToZip(myZipFile,folder_src,folder_dst):
    folder_src = folder_src.encode('ascii') #convert path to ascii for ZipFile Method
    for file in glob.glob(folder_src+"/*"):
        if os.path.isfile(file):
            myZipFile.write(file, folder_dst+os.path.basename(file), zipfile.ZIP_DEFLATED)
        elif os.path.isdir(file):
            addFolderToZip(myZipFile,file,folder_dst+os.path.basename(file)+'/')

# Go through a tar.gz archive, get all the medias from each modules
# module1/ -> img,img... module2/ -> img, img......
def getMediasDataFromArchive(medias, nb_module):

    mediasData=[]
    mediasNom=[]

    if not medias:
        for i in range(1,int(nb_module)+1):
            mediasData.append([])
            mediasNom.append([])
        return mediasData, mediasNom


    tarArchiveIO = StringIO.StringIO()
    tarArchiveIO.write(medias.read())
    tarArchiveIO.seek(0)



    # We open the tar archive inside of the StringIO instance
    with tarfile.open(mode='r:gz', fileobj=tarArchiveIO) as tar:

        #go through the archive files and create the StringIO containing modules and medias
        for i in range(1,int(nb_module)+1):
            mediaData=[]
            mediaNom=[]
            reModuleData = re.compile('^module'+str(i)+'/(?P<nom>.*)$')
            for member in tar.getnames():
                res=reModuleData.match(member)
                if res:
                    media=StringIO.StringIO()
                    media.write(tar.extractfile(member).read())
                    media.seek(0)
                    mediaData.append(media)
                    mediaNom.append(res.groupdict()['nom'])
            mediasData.append(mediaData)
            mediasNom.append(mediaNom)

    tar.close()
    return mediasData,mediasNom




# Write a XML file in string from a Cours Model (only keep module names and url)
def writeXMLCourse(cours):

    coursXML = etree.Element("cours")
    nom = etree.SubElement(coursXML,"nom")
    nom.text = cours.nom_cours
    nbModule = etree.SubElement(coursXML, "nbModule")
    nbModule.text = str(cours.nb_module)

    for module in cours.module_set.all():
        moduleXML = etree.SubElement(coursXML,"module")
        nomModule = etree.SubElement(moduleXML,"nomModule")
        nomModule.text = module.nom_module

    return etree.tostring(coursXML, pretty_print=True)

# pack the markdown files and xml file into a tar archive.
# the user may use it again later for reuploading his course.
def createExportArchive(zipFile):
    # pack it up into a tar archive
    # by using regex to determine which file must be included in that archive
    # (We have to look into the archive being generated)
    tab=zipFile.namelist()
    reExportPath = re.compile('^export/')

    tarArchiveIO = StringIO.StringIO()

    # We open the tar archive inside of the StringIO instance
    with tarfile.open(mode='w:gz', fileobj=tarArchiveIO) as tar:
        #for each EDX element belonging to the module
        for elt in tab:
            res=reExportPath.match(elt)

            if res:
                # adding the file to the tar archive
                # (we need tarInfo and StringIO instance for not writing anything on the disk)
                path=elt.replace('export/','')
                data=zipFile.read(elt)
                info=tarfile.TarInfo(name=path)
                info.size=len(data)
                tar.addfile(tarinfo=info, fileobj=StringIO.StringIO(data))
        tar.close()

    tarArchiveIO.seek(0)
    zipFile.writestr("export/export.tar.gz", tarArchiveIO.read())

    return zipFile


# Build the site and return the archive, used in both forms (either InMemoryUploadedFile or StringIO, both have readable attribute)
def buildSiteLight(course_obj, modulesData, mediasData, mediasNom, homeData, titleData, logoData, xmlCourse):

    inMemoryOutputFile = StringIO.StringIO()
    zipFile = ZipFile(inMemoryOutputFile, 'w')
    addFolderToZip(zipFile,BASE_PATH+'/static/','static/')

    jenv = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    jenv.filters['slugify'] = utils.cnslugify
    site_template = jenv.get_template("site_layout.html")

    ####XML
    zipFile.writestr("export/infos.xml", xmlCourse)

    ####LOGO
    #if found, copy logo.png, else use default
    logo_files=logoData
    if logoData != None:
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
    for module, mediaData, mediaNom in zip(course_obj.modules,mediasData, mediasNom):
        zipFile = toEDX.generateEDXArchiveLight(module, module.module, zipFile)
        zipFile = toIMS.generateImsArchiveLight(module, module.module, zipFile)

        # write html, XML, and JSon files
        file_path=module.module

        if mediaData:
            for media,nom in zip(mediaData, mediaNom):
                zipFile.writestr(file_path+'/media/'+nom, media.read())

        zipFile.writestr(file_path+'/'+module.module+'.questions_bank.gift.txt', module.toGift().encode("UTF-8"))
        zipFile.writestr(file_path+'/'+module.module+'.video_iframe_list.txt', module.toVideoList().encode("UTF-8"))
        mod_config=zipFile.writestr(file_path+'/'+module.module+'.config.json', module.toJson().encode("UTF-8")) # FIXME : this file should be optionnaly written

        module_template = jenv.get_template("module.html")
        module_html_content = module_template.render(module=module)
        html = site_template.render(course=course_obj, module_content=module_html_content, body_class="modules", logo=logo)
        zipFile.writestr(module.module+'.html', html.encode("UTF-8"))

    # write into the archive the different md files
    homeData.seek(0)
    zipFile.writestr('export/home.md',homeData.read())
    i=1
    for moduleData in modulesData:
        zipFile.writestr('export/module'+str(i)+'.md',moduleData.read())
        i=i+1

    # create export archive
    zipFile = createExportArchive(zipFile)

    zipFile.close()
    inMemoryOutputFile.seek(0)

    return inMemoryOutputFile

# Generate an archive from a complete form, contains InMemoryUploadedFile
def generateArchive(modulesData, mediasData, mediasNom, homeData, titleData, logoData, xmlCourse=""):
    modules=[]
    i=1
    for moduleData in modulesData:
        #The only way I could find to encode InMemoryUploadedFile into utf-8 (avoid warning)
        #moduleData = TextIOWrapper(moduleData.file, encoding='utf-8')
        m=processModuleLight("module"+str(i),moduleData)
        modules.append(m)
        moduleData.seek(0)
        i=i+1
    c=processRepositoryLight(modules)

    #mediasDataObj,mediasNom=extractMediaArchive(mediasData, mediaTypes)

    #outputFile=buildSiteLight(c,repoDir,outDir,mediasData,homeData,titleData, logoData)
    outputFile=buildSiteLight(c, modulesData, mediasData,mediasNom,homeData,titleData, logoData, xmlCourse)

    return outputFile

# extract the different medias contained in a tar.gz or a zip archive (used in the complete form and the general application)
# return a couple containing a list of each files of each modules (StringIO), and their names
def extractMediaArchive(mediasData, mediasType):
    mediasDataObj=[]
    mediasNom=[]

    # one iteration correspond to one module
    # We want to extract all the files in StringIO iterations
    for mediaData,mediaType in zip(mediasData,mediasType):
        mediaDataObj=[]
        mediaNom=[]

        # We determine which type is the media archive.
        # Only two forms are accepted now: Zip and Tar.Gz
        # In the other cases, we just skip the file

        # Dealing with tar.gz archive
        if mediaType == 'application/octet-stream':
            tarArchiveIO = StringIO.StringIO()
            tarArchiveIO.write(mediaData.read())
            tarArchiveIO.seek(0)

            # We open the tar archive inside of the StringIO instance
            with tarfile.open(mode='r:gz', fileobj=tarArchiveIO) as tar:
                for member in tar.getnames():
                    media=StringIO.StringIO()
                    media.write(tar.extractfile(member).read())
                    mediaDataObj.append(media)
                    mediaNom.append(member)
                tar.close()
            mediasDataObj.append(mediaDataObj)
            mediasNom.append(mediaNom)

        # Dealing with zip archive
        elif mediaType == 'application/zip':
            zipArchiveIO = StringIO.StringIO()
            zipArchiveIO.write(mediaData.read())
            zipArchiveIO.seek(0)
            with ZipFile(zipArchiveIO, 'r') as zipfile:
                for member in zipfile.namelist():
                    media=StringIO.StringIO()
                    media.write(zipfile.read(member))
                    media.seek(0)
                    mediaDataObj.append(media)
                    mediaNom.append(member)
                zipfile.close()

            mediasDataObj.append(mediaDataObj)
            mediasNom.append(mediaNom)

        # Default case: Nothing is done here
        else:
            mediasDataObj.append(None)
            mediasNom.append(None)

    return mediasDataObj,mediasNom



# put a file from a tarfile object to a StringIO object
def StringIOFromTarFile(tarFile,nomFichier):
    element=StringIO.StringIO();
    element.write(tarFile.extractfile(nomFichier).read())
    element.seek(0)
    return element


# Generate the archive with an entire archive which followed the repository model established before
def generateArchiveLight(archiveData):

    tarArchiveIO = StringIO.StringIO()
    tarArchiveIO.write(archiveData.read())
    tarArchiveIO.seek(0)

    titleData=''
    homeData=StringIO.StringIO()
    erreurs=[]

    # We open the tar archive inside of the StringIO instance
    with tarfile.open(mode='r:gz', fileobj=tarArchiveIO) as tar:

        try:
            titleData=StringIOFromTarFile(tar,'title.md')
            #titleData=tar.extractfile('title.md').read()
        except KeyError:
            erreurs.append("Erreur de structure: Impossible de trouver title.md !");
        try:
            homeData=StringIOFromTarFile(tar,'home.md')
        except KeyError:
            erreurs.append("Erreur de structure: Impossible de trouver home.md !");
        try:
            logoData=StringIOFromTarFile(tar,'logo.png')
        except KeyError:
            erreurs.append("Erreur de structure: Impossible de trouver logo.png !");

        modulesData=[]
        mediasData=[]
        mediasNom=[]

        res = True
        maxModule = -1
        reModule = re.compile('^module(?P<cptModule>\d)')

        # search for the number of modules in the archive
        for member in tar.getnames():
            res = reModule.match(member)
            if(res):
                nbModule = res.groupdict()['cptModule']
                if maxModule < nbModule:
                    maxModule = nbModule

        #go through the archive files and create the StringIO containing modules and medias
        for i in range(1,int(maxModule)+1):
            reModuleData = re.compile('^module'+str(i)+'/.*\.md$')
            reMediaData = re.compile('^module'+str(i)+'/media/(?P<nom>.*)$')
            mediaData=[]
            nomData=[]
            oneModuleFound=False
            for member in tar.getnames():
                res = reModuleData.match(member)
                if res and not oneModuleFound:
                    module=StringIOFromTarFile(tar,member)
                    modulesData.append(module)
                    oneModuleFound=True
                res = reMediaData.match(member)
                if(res):
                    media=StringIOFromTarFile(tar,member)
                    mediaData.append(media)
                    nomData.append(res.groupdict()['nom'])
            if not oneModuleFound:
                erreurs.append("Il manque le module "+str(i)+" !")
            mediasData.append(mediaData)
            mediasNom.append(nomData)


        tar.close()

        ######

        modules=[]
        i=1
        for moduleData in modulesData:
            #The only way I could find to encode InMemoryUploadedFile into utf-8 (avoid warning)
            # moduleData = TextIOWrapper(moduleData.read(), encoding='utf-8')
            m=processModuleLight("module"+str(i),moduleData)
            modules.append(m)
            i=i+1
        c=processRepositoryLight(modules)

        outputFile=""
        if not erreurs:
            outputFile=buildSiteLight(c, modulesData, mediasData, mediasNom, homeData, titleData, logoData, '')

        return outputFile,erreurs
