#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import logging

from django import forms
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

class UploadForm(forms.Form):

    nom_projet = forms.CharField(max_length=100)
    logo = forms.ImageField()
    home = forms.FileField()
    module1 = forms.FileField()
    module2 = forms.FileField()
