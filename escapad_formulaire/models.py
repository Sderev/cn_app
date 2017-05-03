from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.contrib.auth.models import User
#from .models import Profil

class Module(models.Model):
    url=models.CharField(max_length=30)

class Projet(models.Model):
    nom_projet=models.CharField(max_length=30)
    url_home=models.CharField(max_length=30)
    nb_module=models.IntegerField()
    def __str__(self):
        #return "Projet nomme {0}, Profil associe: {1}".format(self.nom_projet, self.profil_set.all())
        return "Projet-> {0}, {1} module(s)".format(self.nom_projet,self.nb_module)

class Profil(models.Model):
    user = models.OneToOneField(User)  # La liaison OneToOne vers le modele User
    #site_web = models.URLField(blank=True)
    projets=models.ManyToManyField(Projet)
    #avatar = models.ImageField(null=True, blank=True, upload_to="avatars/")
    #signature = models.TextField(blank=True)
    #inscrit_newsletter = models.BooleanField(default=False)

    def __str__(self):
        return "Profil de {0}, projets: {1}".format(self.user.username,self.projets.all())
        #return "Profil de {0}".format(self.user.username)
#class
