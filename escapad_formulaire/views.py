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
from django.contrib.auth.forms import PasswordChangeForm


from src import model
from src import utils
from src import cnExportLight as cn

import markdown
import StringIO
import urllib2


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


def inscription(request):
    error = False
    print "oooooooooooooooo"
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        print form.is_valid()
        if form.is_valid():
            #username = form.cleaned_data["username"]
            #password = form.cleaned_data["password"]
            #user = authenticate(username=username, password=password)  # Nous vérifions si les données sont correctes
            print('okay');
            form.save();
            #login(request, user)  # nous connectons l'utilisateur
        else: # sinon une erreur sera affichée
            error = True
    else:
        form = CreateUserForm()

    return render(request, 'escapad_formulaire/inscription.html', locals())

def deconnexion(request):
    logout(request)
    return redirect(reverse(connexion))

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
        titleData=form.cleaned_data["nom_projet"]
        logoData=form.cleaned_data["logo"]

        modulesData=[]
        mediasData=[]
        nbModule=request.POST.get("nb_module")

        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)
            nomMedia="media_"+str(i)
            moduleData=request.FILES.get(nomModule)
            mediaData=request.FILES.get(nomMedia)

            modulesData.append(moduleData)
            mediasData.append(mediaData)

        print mediasData

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



def form_upload_eth(request):
    sauvegarde = False


    form = UploadFormEth(request.POST or None, request.FILES or None)
    formMod = ModuleFormEth(request.POST or None, request.FILES or None)


    print form.is_valid()
    print formMod.is_valid()

    if form.is_valid() and formMod.is_valid():

        repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR


        titleData=form.cleaned_data["nom_projet"]
        logoData=form.cleaned_data["logo"]

        homeDataTmp=request.POST.get("home_data")
        response = urllib2.urlopen(homeDataTmp)
        homeData = StringIO.StringIO(response.read())

        modulesData=[]
        mediasData=[]
        nbModule=request.POST.get("nb_module")

        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)

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


def apercu_module(request,id_export):
    url="http://193.51.236.202:9001/p/"+id_export+"/export/txt"
    print url

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
