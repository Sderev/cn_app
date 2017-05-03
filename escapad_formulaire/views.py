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

import forms

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

        repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR

        homeData=form.cleaned_data["home"]
        titleData=form.cleaned_data["nom_cours"]
        logoData=form.cleaned_data["logo"]

        modulesData=[]
        mediasData=[]
        nbModule=request.POST.get("nb_module")

        #Go through each modules to get the md and media data
        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)
            nomMedia="media_"+str(i)
            moduleData=request.FILES.get(nomModule)
            mediaData=request.FILES.get(nomMedia)

            modulesData.append(moduleData)
            mediasData.append(mediaData)

        zip=cn.generateArchive(modulesData,mediasData,homeData,titleData,logoData,repoDir,outDir,baseUrl)

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
        zip=cn.generateArchiveLight(archiveData, repoDir, outDir, baseUrl)

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
        nbModule=request.POST.get("nb_module")

        #Go through each module to get the md and media data
        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)

            #Get the text from the etherpad instance (see above for explanation)
            moduleDataTmp=request.POST.get(nomModule)
            response = urllib2.urlopen(moduleDataTmp)
            moduleData= StringIO.StringIO(response.read())

            nomMedia="media_"+str(i)
            mediaData=formMod.cleaned_data[nomMedia]

            modulesData.append(moduleData)
            mediasData.append(mediaData)

        zip=cn.generateArchive(modulesData,mediasData,homeData,titleData,logoData,repoDir,outDir,baseUrl)

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response

    return render(request, 'escapad_formulaire/formeth.html', {
        'form': form,
        'formMod': formMod,
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
    url="http://193.51.236.202:9001/p/"+id_export+"/export/txt"
    response = urllib2.urlopen(url)

    moduleData= StringIO.StringIO(response.read())
    print moduleData
    MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
    m = model.Module(moduleData, "module", "base")
    m.toHTML(True)
    home_html=m.toCourseHTMLVisualisation()

    return render(request, 'escapad_formulaire/apercu.html', {
        'res': home_html
    })

# View showing the preview of a home page using the culture-numerique css
# require the pad id
def apercu_home(request,id_export):
    url="http://193.51.236.202:9001/p/"+id_export+"/export/txt"
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
    print request
    myUser=request.user
    profil= Profil.objects.get(user=myUser)
    form = CreateNew(request.POST or None)
    print myUser.first_name
    if form.is_valid() :
        url_home='home-'+id_generator()
        id_cours=id_generator()
        cours=Cours(id_cours=id_cours, nom_cours=form.cleaned_data['nom'], nb_module=1, url_home=url_home)
        cours.save()
        profil.cours.add(cours)
        #url_home='http://193.51.236.202:9001/p/'+url_home

    return render(request, 'escapad_formulaire/liste_cours.html', {
        'profil' : profil,
        'form' : form
    })

# View
def cours(request, id_cours):

    cours= Cours.objects.get(id_cours=id_cours)
    form = CreateNew(request.POST or None)
    if form.is_valid() :
        url='module-'+id_generator()
        module=Module(nom_module=form.cleaned_data['nom'], url=url, cours=cours)
        module.save()


    form2 = UploadFormEth(request.POST or None, request.FILES or None)
    if form2.is_valid() :

        repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR

        titleData=form2.cleaned_data["nom_cours"]
        logoData=form2.cleaned_data["logo"]

        #print cours.url_home
        url_home='http://193.51.236.202:9001/p/'+cours.url_home+'/export/txt'


        # Get the text from the etherpad instance
        # We need to create a hidden input storing the plain text exporting url.
        # The url looks like this: http://<etherpad-url>/p/<pad-url>/export/txt
        response = urllib2.urlopen(url_home)
        homeData = StringIO.StringIO(response.read())

        modulesData=[]
        mediasData=[]

        for module in cours.module_set.all():
            url_module= 'http://193.51.236.202:9001/p/'+module.url+'/export/txt'
            response = urllib2.urlopen(url_module)
            moduleData = StringIO.StringIO(response.read())
            #print moduleData.read()
            modulesData.append(moduleData)
            mediasData.append('')



        #homeData=""

        zip=cn.generateArchive(modulesData,mediasData,homeData,titleData,logoData,repoDir,outDir,baseUrl)

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response


    cours=Cours.objects.get(id_cours=id_cours)
    print cours.nom_cours
    return render(request, 'escapad_formulaire/cours.html', {
        'cours' : cours,
        'form' : form,
        'form2' : form2
    })

# View form for creating the home file
def cours_edition(request, id_cours ,url):


    #url_home='home-'+id_generator()
    full_url='http://193.51.236.202:9001/p/'+url




    return render(request, 'escapad_formulaire/form_edition.html', {
        'id_cours': id_cours,
        'url': url,
        'full_url': full_url,
        'sauvegarde': False
    })



def delete_module(request, id_cours, url):
    module= Module.objects.get(url=url)
    module.delete()
    return redirect(cours,id_cours=id_cours)

def delete_course(request, id_cours):
    course= Cours.objects.get(id_cours=id_cours)
    course.delete()
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
    print "oooooooooooooooo"
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
