#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import logging

from django import forms
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)



class RepositoryForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(RepositoryForm, self).clean()
        print("cleaned_data = %s " % cleaned_data)
        success = True
        if cleaned_data['git_url']:
            try:
                res = requests.get(cleaned_data['git_url'])
                if not (res.status_code == 200):
                    success = False
            except Exception as e:
                logger.error("Error when checking url \n\t %s" % (e))
                success = False
            if not success:
                raise forms.ValidationError(
                    _('Git URL invalide %(url)s '),
                    code='invalid_url',
                    params={'url': cleaned_data['git_url'] },
                )
            else:
                return
