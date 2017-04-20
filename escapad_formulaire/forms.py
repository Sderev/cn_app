#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import logging

from django import forms
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

class UploadForm(forms.Form):

    nom_projet = forms.CharField(max_length=100)
    logo = forms.ImageField(required=False)
    home = forms.FileField()
    #module1 = forms.FileField()
    #module2 = forms.FileField()

class ModuleForm(forms.Form):
    module_1 = forms.FileField()
    media_1 = forms.FileField(required=False)

class UploadFormLight(forms.Form):

    archive=forms.FileField()
