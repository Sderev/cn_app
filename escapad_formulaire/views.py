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

from src import model
from src import utils
from src import cnExportLight as cn

import markdown


def form_upload(request):
    sauvegarde = False

    form = UploadForm(request.POST or None, request.FILES or None)

    if form.is_valid():
    	#print type(form.cleaned_data["home"])

    	repoDir=settings.BASE_DIR
    	outDir=settings.BASE_DIR
    	baseUrl=settings.BASE_DIR

        moduleData=form.cleaned_data["module"]
        homeData=form.cleaned_data["home"]

        modulesData=[]
        modulesData.append(moduleData)

        html=cn.generateArchive(modulesData,homeData,repoDir,outDir,baseUrl)

        sauvegarde = True
        return HttpResponse(html)

    return render(request, 'escapad_formulaire/form.html', {
        'form': form,
        'sauvegarde': sauvegarde
    })
