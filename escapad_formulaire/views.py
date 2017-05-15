#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import mimetypes
import logging
import os
import shlex
import subprocess
import sys
import tarfile

import forms
from lxml import etree

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic import View

from django.contrib.auth import authenticate, login, logout

logger = logging.getLogger(__name__)

from .forms import *
from .models import *
from django.contrib.auth.forms import PasswordChangeForm


from src import model
from src import utils
from src import cnExportLight as cn

import markdown
import StringIO
import urllib2

#RANDOM
import string
import random
import re
from cn_app.settings import ETHERPAD_URL
from cn_app.settings import API_KEY


#################################
#                               #
#        SIMPLE FORMS VIEWS     #
#                               #
#################################

# View creating archive using a simple form with inputs only (no etherpad)
# Each module is composed of a markdown file, and a media folder
def form_upload(request):
    sauvegarde = False
    print request.user.username

    form = UploadForm(request.POST or None, request.FILES or None)
    formMod = ModuleForm(request.POST or None, request.FILES or None)

    if form.is_valid() and formMod.is_valid():

        homeData=form.cleaned_data["home"]
        titleData=form.cleaned_data["nom_cours"]
        logoData=form.cleaned_data["logo"]

        modulesData=[]
        mediasData=[]
        mediasType=[]
        nbModule=request.POST.get("nb_module")

        #Go through each modules to get the md and media data
        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)
            nomMedia="media_"+str(i)
            moduleData=request.FILES.get(nomModule)
            mediaData=request.FILES.get(nomMedia)

            modulesData.append(moduleData)
            mediasData.append(mediaData)

            # Specify if the media is empty or not (tar.gz or empty)
            #TODO No zip supported for now (Improve?)
            if mediaData:
                mediasType.append('application/octet-stream')
            else:
                mediasType.append('None')

        mediasDataObj,mediasNom=cn.extractMediaArchive(mediasData, mediasType)

        zip=cn.generateArchive(modulesData,mediasDataObj,mediasNom,homeData,titleData,logoData,"")

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response

    return render(request, 'escapad_formulaire/form.html', {
        'form': form,
        'formMod': formMod,
        'sauvegarde': sauvegarde
    })

# View requesting an archive already made by the user
# Generate directly the website
def form_upload_light(request):
    sauvegarde = False

    form = UploadFormLight(request.POST or None, request.FILES or None)

    if form.is_valid() :
        repoDir=settings.BASE_DIR
        outDir=settings.BASE_DIR
        baseUrl=settings.BASE_DIR

        archiveData=form.cleaned_data["archive"]
        zip=cn.generateArchiveLight(archiveData)

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response

    return render(request, 'escapad_formulaire/formlight.html', {
        'form': form,
        'sauvegarde': sauvegarde
    })



# View dealing with etherpad instances
# This view was used for testing the etherpad viability
# Nothing is stored in models, the view creates dynamically etherpad instances when the user wants to add a module
def form_upload_eth(request):
    sauvegarde = False

    form = UploadFormEth(request.POST or None, request.FILES or None)
    formMod = ModuleFormEth(request.POST or None, request.FILES or None)

    if form.is_valid() and formMod.is_valid():

        repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR

        titleData=form.cleaned_data["nom_cours"]
        logoData=form.cleaned_data["logo"]

        # Get the text from the etherpad instance
        # We need to create a hidden input storing the plain text exporting url.
        # The url looks like this: http://<etherpad-url>/p/<pad-url>/export/txt
        homeDataTmp=request.POST.get("home_data")
        response = urllib2.urlopen(homeDataTmp)
        homeData = StringIO.StringIO(response.read())

        modulesData=[]
        mediasData=[]
        mediasType=[]
        nbModule=request.POST.get("nb_module")

        #Go through each module to get the md and media data
        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)

            #Get the text from the etherpad instance (see above for explanation)
            moduleDataTmp=request.POST.get(nomModule)
            response = urllib2.urlopen(moduleDataTmp)
            moduleData= StringIO.StringIO(response.read())

            nomMedia="media_"+str(i)
            mediaData=request.POST.get(nomMedia)

            modulesData.append(moduleData)
            mediasData.append(mediaData)

            #Specify if the media is empty or not (tar.gz or empty)
            if mediaData:
                mediasType.append('application/octet-stream')
            else:
                mediasType.append('None')

        zip=cn.generateArchive(modulesData,mediasData,mediasType,homeData,titleData,logoData,repoDir,outDir,baseUrl)

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response

    return render(request, 'escapad_formulaire/formeth.html', {
        'ETHERPAD_URL' : ETHERPAD_URL,
        'form': form,
        'formMod': formMod,
        'sauvegarde': sauvegarde
    })


# View allowing the user to reupload a course with the export.tar.gz provided when generating a course
def form_reupload(request):

    if not request.user.is_authenticated:
        return redirect(connexion)

    myUser=request.user
    profil= Profil.objects.get(user=myUser)

    sauvegarde = False

    form = UploadFormLight(request.POST or None, request.FILES or None)

    if form.is_valid() :
        repoDir=settings.BASE_DIR
        outDir=settings.BASE_DIR
        baseUrl=settings.BASE_DIR

        tarArchiveIO = StringIO.StringIO(form.cleaned_data["archive"].read())

        # We open the tar archive inside of the StringIO instance
        with tarfile.open(mode='r:gz', fileobj=tarArchiveIO) as tar:
            #for each EDX element belonging to the module

            print tar.getnames()
            xmlFile = tar.extractfile("infos.xml")
            tree = etree.parse(xmlFile)

            # Get the course infos
            cours=tree.xpath("/cours")[0]
            nom=cours.getchildren()[0].text
            #url_media=cours.getchildren()[1].text
            nb_module=cours.getchildren()[2].text
            if url_media == None :
                url_media = ''

            # Generate the course and associate with the current user
            id_cours = id_generator()
            url_home = 'home-'+id_generator()
            #cours_obj = Cours(nom_cours=nom, id_cours=id_cours, url_home=url_home, url_media=url_media, nb_module=nb_module)
            cours_obj = Cours(nom_cours=nom, id_cours=id_cours, url_home=url_home, nb_module=nb_module)
            cours_obj.save()
            profil.cours.add(cours_obj)
            profil.save()

            # Generate each media
            cpt=1
            for nomMod, urlMediaMod in zip(tree.xpath("/cours/module/nomModule"),tree.xpath("/cours/module/urlMedia")):
                moduleFile= tar.extractfile("module"+str(cpt)+".md")
                url = 'module-'+id_generator()
                nom_module = nomMod.text
                url_media = urlMediaMod.text
                if url_media == None :
                    url_media = ''
                module_obj = Module(url=url, nom_module=nom_module, url_media=url_media, cours=cours_obj)
                module_obj.save()

                os.system("curl -X POST -H 'X-PAD-ID:"+ url +"' " +ETHERPAD_URL+"post")
                os.system("curl -X POST --data '"+moduleFile.read()+"' -H 'X-PAD-ID:"+ url +"' " +ETHERPAD_URL+"post")

                cpt+=1

            tar.close()

        return redirect(mes_cours)

    return render(request, 'escapad_formulaire/formreupload.html', {
        'form': form,
        'sauvegarde': sauvegarde
    })

######################################
#                                    #
#           PREVIEW VIEWS            #
#                                    #
######################################


# View showing the preview of a module using the culture-numerique css
# require the pad id
def apercu_module(request,id_export):
    url=ETHERPAD_URL+"p/"+id_export+"/export/txt"
    response = urllib2.urlopen(url)

    moduleData= StringIO.StringIO(response.read())
    print moduleData
    MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
    module = model.Module(moduleData, "module", "base")
    #m.toHTML(True)
    #home_html=m.toCourseHTMLVisualisation()

    home_html = ''
    for sec in (module.sections):
        #print 'sec'
        home_html += "\n\n<!-- Section "+sec.num+" -->\n"
        home_html += "\n\n<h1> "+sec.num+". "+sec.title+" </h1>\n";
        for sub in (sec.subsections):
            home_html += "\n\n<!-- Subsection "+sub.num+" -->\n"
            home_html += "\n\n<h2>"+sub.num+". "+sub.title+" </h2>\n"
            #home_html += markdown.markdown(sub.src, MARKDOWN_EXT)
            #print 'sub'
            #print sub
            #print sub.toHTML(True)
            home_html += sub.toHTML(True)

    return render(request, 'escapad_formulaire/apercu.html', {
        'res': home_html
    })

# View showing the preview of a home page using the culture-numerique css
# require the pad id
def apercu_home(request,id_export):
    url=ETHERPAD_URL+"p/"+id_export+"/export/txt"
    print url

    response = urllib2.urlopen(url)

    moduleData= response.read()
    print moduleData
    MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
    home_html = markdown.markdown(moduleData, MARKDOWN_EXT)

    return render(request, 'escapad_formulaire/apercu.html', {
        'res': home_html
    })


#################################
#                               #
#         FORMS WITH MODEL      #
#                               #
#################################

# id generator for the projects
def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# View resuming the user's courses
# The user can either access an existing course, or create a new one
def mes_cours(request):

    if not request.user.is_authenticated:
        return redirect(connexion)

    myUser=request.user
    profil= Profil.objects.get(user=myUser)
    form = CreateNew(request.POST or None)
    print myUser.first_name
    if form.is_valid() :
        url_home='home-'+id_generator()
        id_cours=id_generator()
        cours=Cours(id_cours=id_cours, nom_cours=form.cleaned_data['nom'], nb_module=0, url_home=url_home)
        cours.save()
        profil.cours.add(cours)

    return render(request, 'escapad_formulaire/liste_cours.html', {
        'profil' : profil,
        'form' : form
    })




# View showing the information of a course
def cours(request, id_cours):

    try:
        cours = Cours.objects.get(id_cours=id_cours)
        request.user.profil.cours.get(id_cours=id_cours)
    except Cours.DoesNotExist:
        return redirect(mes_cours)

    #if not request.user.profil.cours.get(id_cours=id_cours):
    #    return redirect(mes_cours)

    form = CreateNew(request.POST or None)
    form2 = GenerateCourseForm(request.POST or None, request.FILES or None)
    form3 = SearchUser(request.POST or None)

    userFound = False

    # Create a new module
    if form.is_valid() and request.POST['id_form'] == '0':
        url = 'module-'+id_generator()
        nom=request.POST['nom']
        module = Module(nom_module=nom, url=url, cours=cours)
        module.save()
        cours.nb_module=cours.nb_module+1
        cours.save()

    # Adding a user to the course
    elif form3.is_valid() and request.POST['id_form'] == '1':
        user = User.objects.get(username = form3.cleaned_data['user'])
        profil = user.profil
        profil.cours.add(cours)
        userFound = True

    # Generating the course
    elif form2.is_valid() and request.POST['id_form'] == '2':
        repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR

        titleData=cours.nom_cours
        logoData=form2.cleaned_data["logo"]
        medias=form2.cleaned_data["medias"]

        url_home=ETHERPAD_URL+'p/'+cours.url_home+'/export/txt'


        # Get the text from the etherpad instance
        # We need to create a hidden input storing the plain text exporting url.
        # The url looks like this: http://<etherpad-url>/p/<pad-url>/export/txt
        response = urllib2.urlopen(url_home)
        homeData = StringIO.StringIO(response.read())

        modulesData=[]
        mediasData=[]
        mediasType=[]

        #for each modules from the course
        for module in cours.module_set.all():
            # get the pad content
            url_module= ETHERPAD_URL+'p/'+module.url+'/export/txt'
            response = urllib2.urlopen(url_module)
            moduleData = StringIO.StringIO(response.read())
            modulesData.append(moduleData)

            """
            # open the dropbox link to get the archive
            url_media=module.url_media
            if(url_media):
                response = urllib2.urlopen(url_media)

                # get the media archive type of content (we try to get either application/zip or application/octet-stream)
                http_message=response.info()
                full=http_message.type
                mediasType.append(full)

                # read the response and add it to the media datas
                mediaData = StringIO.StringIO(response.read())
                mediasData.append(mediaData)
            else:
                mediasData.append(None)
                mediasType.append(None)
            """
            #mediasData.append(None)
            #mediasType.append(None)
        mediasData, mediasNom=cn.getMediasDataFromArchive(medias, len(cours.module_set.all()))

        xmlCourse=cn.writeXMLCourse(cours)
        #zip=cn.generateArchive(modulesData,mediasData,mediasType,homeData,titleData,logoData,repoDir,outDir,baseUrl, xmlCourse)
        zip=cn.generateArchive(modulesData,mediasData,mediasNom,homeData,titleData,logoData, xmlCourse)
        #zip=""

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response




    cours=Cours.objects.get(id_cours=id_cours)

    return render(request, 'escapad_formulaire/cours.html', {
        'cours' : cours,
        'form' : form,
        'form2' : form2,
        'form3' : form3,
        'userFound' : userFound

    })

# View form for creating the home file
def cours_edition(request, id_cours ,url):

    if not request.user.is_authenticated:
        return redirect(connexion)

    # Check if the user has the right to be on this page
    try:
        cours = Cours.objects.get(id_cours=id_cours)
        request.user.profil.cours.get(id_cours=id_cours)
    except Cours.DoesNotExist:
        return redirect(mes_cours)

    is_home=True
    name=''
    # url starting with module: check it it belongs to the course
    if re.match(r"^module",url):
        # Check if the module exists
        try:
            module=cours.module_set.get(url=url)
        except Module.DoesNotExist:
            return redirect(mes_cours)
        name=module.nom_module
        #url_media = module.url_media
        is_home = False
    # url starting with home: check if it is equal to the course url_home
    elif re.match(r"^home",url):
        name="home"
        #url_media = cours.url_media
        if cours.url_home != url:
            return redirect(mes_cours)
    # the url doesn't start with "home" nor "module", there is no chance it belongs to the application
    else:
        return redirect(mes_cours)

    full_url = ETHERPAD_URL+'p/'+url

    """
    form_media = MediaForm(request.POST or None)
    #if we changed the media url
    if form_media.is_valid() :
        res_url=form_media.cleaned_data['url_media']
        #if the url if from dropbox, we change dl=0 to dl=1, in order to create a direct download link
        # (not provided by dropbox directly), I guess it's better to do it rather than asking the user.
        if re.match(r"^.*dropbox.*dl=",res_url):
            res_url=re.sub(r"^(?P<debut>.*)dl=[0-9](?P<fin>.*)$", r"\g<debut>dl=1\g<fin>", res_url)

        url_media=''
        #If we modify the home page
        if re.match(r"^home",url):
            cours.url_media=res_url
            cours.save()
            url_media= cours.url_media
        #If we modify a module page
        elif re.match(r"^module",url):
            module=Module.objects.get(url=url)
            module.url_media=res_url
            module.save()
            url_media= module.url_media
    """

    return render(request, 'escapad_formulaire/form_edition.html', {
        'id_cours': id_cours,
        'url': url,
        'full_url': full_url,
        #'url_media': url_media,
        #'form_media': form_media,
        'name': name,
        'is_home': is_home
    })

# Delete a module from a course
# Irreversible task
def delete_module(request, id_cours, url):
    if not request.user.is_authenticated:
        return redirect(connexion)

    # Check if the course exists
    try:
        course = Cours.objects.get(id_cours=id_cours)
        request.user.profil.cours.get(id_cours=id_cours)
    except Cours.DoesNotExist:
        return redirect(mes_cours)

    # Check if the module exists
    try:
        module=course.module_set.get(url=url)
        #module= Module.objects.get(url=url)
    except Module.DoesNotExist:
        return redirect(mes_cours)

    # Delete the pad
    response = urllib2.urlopen("http://193.51.236.202:9001/api/1/deletePad?apikey="+API_KEY+"&padID="+url)

    # Delete the module model and update the course model
    module.delete()
    c= Cours.objects.get(id_cours=id_cours)
    c.nb_module=c.nb_module-1
    c.save()
    return redirect(cours,id_cours=id_cours)


# Delete a course, then redirect the user to its course list page
# Note: If a course is shared by several user, the course will not be deleted,
# we will just remove the ManyToManyField relation between the user and the course
def delete_course(request, id_cours):
    if not request.user.is_authenticated:
        return redirect(connexion)

    # Check if the course exists
    try:
        course = Cours.objects.get(id_cours=id_cours)
        request.user.profil.cours.get(id_cours=id_cours)
    except Cours.DoesNotExist:
        return redirect(connexion)

    # delete the home pad
    response = urllib2.urlopen("http://193.51.236.202:9001/api/1/deletePad?apikey="+API_KEY+"&padID="+course.url_home)

    # Only one contributor to the course: We delete it entirely.
    if len(course.profil_set.all()) == 1:
        # delete the pads belonging to the course
        for module in course.module_set.all():
            response = urllib2.urlopen("http://193.51.236.202:9001/api/1/deletePad?apikey="+API_KEY+"&padID="+module.url)
            module.delete()
        course.delete()
    # More than one contributor: We remove the link between the current user and the course.
    else:
        profil=request.user.profil
        course.profil_set.remove(profil)
    return redirect(mes_cours)


#################################
#                               #
#  CONNEXION AND SUBSCRIPTION   #
#                               #
#################################



# Connexion View
def connexion(request):
    error = False
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # Nous vérifions si les données sont correctes
            if user:  # Si l'objet renvoyé n'est pas None
                login(request, user)  # nous connectons l'utilisateur
            else: # sinon une erreur sera affichée
                error = True
    else:
        form = ConnexionForm()

    return render(request, 'escapad_formulaire/connexion.html', locals())

# View for creating a new user on the user side
# The form create a user (Django native class), and associate him to a profile, which will contain the user's projects
def inscription(request):
    error = False
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        print form.is_valid()
        if form.is_valid():
            form.save();
            return redirect(connexion)
        else: # sinon une erreur sera affichée
            error = True
    else:
        form = CreateUserForm()

    return render(request, 'escapad_formulaire/inscription.html', locals())

# Disconnecting view
def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))
