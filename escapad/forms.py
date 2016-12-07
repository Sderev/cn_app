#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import logging

from django import forms
from django.utils.translation import ugettext as _

from .models import Repository

logger = logging.getLogger(__name__)

class RepositoryForm(forms.ModelForm):

    def clean(self):
        """Clean is called right after submitting form and before performing actual submission
        We override it to check the git url provided given url returns a 200 response
        """
        cleaned_data = super(RepositoryForm, self).clean()
        # Process check only when adding object. In the edit admin page 'git_url' is set as read-only and hence is not loaded in the form validation object
        if not self.instance.git_url:
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
