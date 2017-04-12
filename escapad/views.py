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

from .models import Repository
from .utils import run_shell_command
logger = logging.getLogger(__name__)

from .forms import UploadForm

from .models import Projet
from .models import Home
from src import model
from src import utils
import markdown

class BuildView(View):
    """
    A view for generating site from Repository
    """
    http_method_names = ['get', 'post']

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(BuildView, self).dispatch(*args, **kwargs)

    def build_repo(self, slug, request):
        # 1. cd to repo path
        repo_path = os.path.join(settings.REPOS_DIR, slug)
        build_path = os.path.join(settings.GENERATED_SITES_DIR, slug)
        base_url = os.path.join(settings.GENERATED_SITES_URL, slug)
        logger.warn("%s | Post to buidl view ! repo_path = %s | Base URL = %s" % (timezone.now(), repo_path, base_url))

        repo_object = Repository.objects.all().filter(slug=slug)[0]
        try:
            os.chdir(repo_path)
        except Exception as e:
            return {"success":"false", "reason":"repo not existing, or not synced"}

        # 2. git pull origin [branch:'master']
        git_cmds = [("git checkout %s " %  repo_object.default_branch), ("git pull origin %s" % repo_object.default_branch)]
        for git_cmd in git_cmds:
            success, output = run_shell_command(git_cmd)
            if not(success):
                os.chdir(settings.BASE_DIR)
                return {"success":"false", "reason":output}

        # 3. build with BASE_PATH/src/toHTML.py
        os.chdir(settings.BASE_DIR)
        build_cmd = ("python src/cnExport.py -r %s -d %s -u %s -i -e" % (repo_path, build_path, base_url))
        success, output = run_shell_command(build_cmd)
        # go back to BASE_DIR and check output
        os.chdir(settings.BASE_DIR)
        # FIXME: output should not be displayed for security reasons, since it is logged internaly to debug.log
        if success:
            repo_object.last_compiled = datetime.datetime.now()
            repo_object.save()
            return({"success":"true", "output":output})
        else:
            return {"success":"false", "reason":output}

    def post(self, request, slug, *args, **kwargs):
        res = self.build_repo(slug, request)
        return JsonResponse(res)

    def get(self, request, slug, *args, **kwargs):
        self.build_repo(slug, request)
        return redirect(reverse('visit_site', args=(slug,)))

def visit_site(request, slug):
    """ Just a redirection to generated site """
    return redirect(os.path.join(settings.GENERATED_SITES_URL, slug, 'index.html'))

def index(request):
    # FIXME : useless now
    return HttpResponse(u"Liste des dépôt")

#def form_upload(request):

"""
def form_upload(request):
    # Construire le formulaire, soit avec les données postées,
    # soit vide si l'utilisateur accède pour la première fois
    # à la page.
    form = forms.ContactForm(request.POST or None)
    # Nous vérifions que les données envoyées sont valides
    # Cette méthode renvoie False s'il n'y a pas de données 
    # dans le formulaire ou qu'il contient des erreurs.
    if form.is_valid(): 
        # Ici nous pouvons traiter les données du formulaire
        sujet = form.cleaned_data['sujet']
        message = form.cleaned_data['message']
        envoyeur = form.cleaned_data['envoyeur']
        renvoi = form.cleaned_data['renvoi']

        # Nous pourrions ici envoyer l'e-mail grâce aux données 
        # que nous venons de récupérer
        envoi = True
    
    # Quoiqu'il arrive, on affiche la page du formulaire.
    return render(request, 'escapad/form.html', locals())
"""

def form_upload(request):
    from jinja2 import Template, Environment, FileSystemLoader
    sauvegarde = False
    
    form = UploadForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():  
	#print type(form.cleaned_data["home"])
	
	repoDir=settings.BASE_DIR	
	outDir=settings.BASE_DIR
	baseUrl=settings.BASE_DIR	

	MARKDOWN_EXT = ['markdown.extensions.extra', 'superscript']
	BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
	TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates' )
	LOGFILE = 'logs/cnExport.log'	
	
	#################
	##    module   ##
	#################

	module= "module1"
	moduleDir = os.path.join(repoDir, module)

	#filein = utils.fetchMarkdownFile(moduleDir)
        #with open(form.cleaned_data["home"], encoding='utf-8') as md_file:
        md_file=form.cleaned_data["module"]
        m = model.Module(md_file, module, baseUrl)	

	print "baseurl" 
	print m.base_url
        m.toHTML(True) # only generate html for all subsections

	
	#####################
	##    course_obj   ##
	#####################
	
	#creation course_obj
	course_obj = model.CourseProgram(repoDir)
	course_obj.modules.append(m)
	
	
    ###################
	## la page index ##
	###################
	
	custom_home = False
        try:
            f = form.cleaned_data["home"]
            #home_file = os.path.join(repoDir, 'home.md')
            #with open(home_file, 'r', encoding='utf-8') as f:
            home_data = f.read()
            home_html = markdown.markdown(home_data, MARKDOWN_EXT)
            custom_home = True
	       
	except Exception as err:
            ## use default from template
            logging.error(" Cannot parse home markdown ")
            with open(os.path.join(TEMPLATES_PATH, 'default_home.html'), 'r', encoding='utf-8') as f:
                home_html = f.read()
	
        
	
	##########################
	## Generation des pages ##
	##########################

	
	logo = 'default'

	jenv = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
        jenv.filters['slugify'] = utils.cnslugify
	site_template = jenv.get_template("site_layout.html")
	
	### generation index
	
	## write index.html file
        html = site_template.render(course=course_obj, module_content=home_html,body_class="home", logo=logo, custom_home=custom_home)
        #utils.write_file(html, os.getcwd(), outDir, 'index.html')

	### generation module
	# Loop through modules
    	for module in course_obj.modules:
            module_template = jenv.get_template("module.html")
            module_html_content = module_template.render(module=module)
            html = site_template.render(course=course_obj, module_content=module_html_content, body_class="modules", logo=logo)
            #utils.write_file(html, os.getcwd(), outDir, module.module+'.html')
	return HttpResponse(html)

	sauvegarde = True
    return render(request, 'escapad/form.html', {
        'form': form, 
        'sauvegarde': sauvegarde
    })

