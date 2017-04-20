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

logger = logging.getLogger(__name__)

from .forms import UploadForm
from .forms import ModuleForm
from .forms import UploadFormLight

from src import model
from src import utils
from src import cnExportLight as cn

import markdown


def form_upload(request):
    sauvegarde = False

    form = UploadForm(request.POST or None, request.FILES or None)
    formMod = ModuleForm(request.POST or None, request.FILES or None)
    #formMod2 = ModuleForm(request.POST or None, request.FILES or None)

    #if form.is_valid() and formMod1.is_valid() and formMod2.is_valid():


    if form.is_valid() and formMod.is_valid():

        #print form.cleaned_data["moduletest"]

        repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR

        homeData=form.cleaned_data["home"]
        titleData=form.cleaned_data["nom_projet"]
        logoData=form.cleaned_data["logo"]

        modulesData=[]
        mediasData=[]
        nbModule=request.POST.get("nb_module")
        #print request.POST
        #print request.FILES

        for i in range(1, int(nbModule)+1):
            nomModule="module_"+str(i)
            nomMedia="media_"+str(i)
            moduleData=request.FILES.get(nomModule)
            mediaData=request.FILES.get(nomMedia)

            modulesData.append(moduleData)
            mediasData.append(mediaData)

        print mediasData

        #modulesData.append(moduleData2)

        zip=cn.generateArchive(modulesData,mediasData,homeData,titleData,logoData,repoDir,outDir,baseUrl)

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response

        #return HttpResponse(zip)"""

    return render(request, 'escapad_formulaire/form.html', {
        'form': form,
        'formMod': formMod,
        'sauvegarde': sauvegarde
    })


def form_upload_light(request):
    sauvegarde = False

    form = UploadFormLight(request.POST or None, request.FILES or None)

    if form.is_valid() :
        #print form.cleaned_data["moduletest"]
        repoDir=settings.BASE_DIR
        outDir=settings.BASE_DIR
        baseUrl=settings.BASE_DIR

        archiveData=form.cleaned_data["archive"]

        #modulesData.append(moduleData2)
        zip=cn.generateArchiveLight(archiveData, repoDir, outDir, baseUrl)

        sauvegarde = True

        response= HttpResponse(zip)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment; filename=\"site.zip\""
        return response

        #return HttpResponse(zip)"""

    return render(request, 'escapad_formulaire/formlight.html', {
        'form': form,
        'sauvegarde': sauvegarde
    })
