#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import re
import subprocess

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

#regexs
reGit = re.compile('http[s]*://(?P<provider>.*?)/(?P<user>.*?)/(?P<repo>[^/]*?)(/|$)')

class Repository(models.Model):

    @staticmethod
    def set_slug(url):
        try:
            slug = slugify(url.rstrip('/').lstrip('htpps://').replace('.','-').replace('/','_').lower())
        except Exception as e:
            slug = slugify(url)
        return slug

    def save(self, *args, **kwargs):
        """ populate some fields from git url before saving, but only when creating new objects"""
        if self.pk is None:#this is true when object does not exist yet
            # use regex to retrieve infos
            fieldsReg = reGit.search(self.git_url)
            if fieldsReg:
                self.git_name = fieldsReg.group('repo') if fieldsReg.group('repo') else "default_name"
                self.git_username = fieldsReg.group('user') if fieldsReg.group('user') else "default_user"
                self.provider = fieldsReg.group('provider') if fieldsReg.group('provider') else "github.com"
            self.slug = self.set_slug(self.git_url)
        super(Repository, self).save(*args, **kwargs)

    git_url = models.URLField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    git_name = models.CharField(max_length=200, blank=True, null=True)
    git_username = models.CharField(max_length=200, blank=True, null=True)
    default_branch = models.CharField(max_length=200, blank=True, null=True, default="master")
    last_compiled = models.DateTimeField(blank=True, null=True)
    repo_synced = models.BooleanField(default=False)
    show_feedback = models.BooleanField(default=False)
    provider = models.URLField(max_length=200, blank=True, null=True)
