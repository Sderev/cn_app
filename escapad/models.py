#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import subprocess

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

# Create your models here.

class Repository(models.Model):
            
    def set_name(self, url):
        try:
            name = url.strip('/').rsplit('/',1)[-1].strip('.git').lower()
        except Exception as e:
            name = "default_name"
        return name
    
    def set_user(self, url):
        try:
            user = url.strip('/').rsplit('/', 2)[-2].lower()
        except Exception as e:
            user = "default_user"
        return user
    
    def set_provider(self, url):
        try:
            provider = url.strip('/').rsplit('/', 3)[-3].lower()
        except Exception as e:
            provider = "http://github.com"
        return provider
    
    @staticmethod    
    def set_slug(url):
        try:
            slug = slugify(url.lstrip('htpps://').replace('.','_').replace('/','__').lower())
        except Exception as e:
            slug = slugify(url)
        return slug
            
    def save(self, *args, **kwargs):
        """ populate some fields from git url before saving"""
        self.git_name = self.set_name(self.git_url)
        self.git_username = self.set_user(self.git_url)
        self.provider = self.set_provider(self.git_url)
        self.slug = self.set_slug(self.git_url)
        super(Repository, self).save(*args, **kwargs)

    git_url = models.URLField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    git_name = models.CharField(max_length=200, blank=True, null=True)
    git_username = models.CharField(max_length=200, blank=True, null=True)
    default_branch = models.CharField(max_length=200, blank=True, null=True, default="master")
    last_compiled = models.DateTimeField(blank=True, null=True)
    repo_synced = models.BooleanField(default=False)
    provider = models.URLField(max_length=200, blank=True, null=True)

class Media(models.Model):
    url = models.FileField()
    def __str__(self):
        return self.url

class Module(models.Model):
    url = models.FileField()#fichier .md
    medias = models.ManyToManyField(Media)
    def __str__(self):
        return self.url

class Home(models.Model):
    url = models.FileField()#fichier .md
    logo = models.ImageField()
    #hasLogo = models.BooleanField(initial=True)
    def __str__(self):
        return self.url

class Projet(models.Model):
    nom = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    home = models.OneToOneField(Home)        
    def __str__(self):
        return self.nom




