"""cn_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
#from escapad import views
import escapad,escapad_formulaire
import escapad_formulaire.views as escapad_form_view
from django.contrib.auth import views as auth_views


urlpatterns = [
    #url(r'', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^form_upload/$', escapad_formulaire.views.form_upload, name='form_upload'),
    url(r'^form_upload_light/$', escapad_formulaire.views.form_upload_light, name='form_upload_light'),
    url(r'^form_upload_eth/$', escapad_formulaire.views.form_upload_eth, name='form_upload_eth'),
    url(r'^apercu_module/(?P<id_export>[-a-zA-Z\d]+)$', escapad_formulaire.views.apercu_module, name='apercu_module'),
    url(r'^apercu_home/(?P<id_export>[-a-zA-Z\d]+)$', escapad_formulaire.views.apercu_home, name='apercu_home'),
    url(r'^connexion/$', escapad_formulaire.views.connexion, name='connexion'),
    url(r'^deconnexion/$', escapad_formulaire.views.deconnexion, name='deconnexion'),
    url(r'^inscription/$', escapad_formulaire.views.inscription, name='inscription'),

    url(r'^reupload/$', escapad_formulaire.views.form_reupload, name='form_reupload'),

    url(r'^cours/$', escapad_formulaire.views.mes_cours, name='mes_cours'),
    url(r'^cours/(?P<id_cours>[-a-zA-Z\d]+)$', escapad_formulaire.views.cours, name='cours'),
    url(r'^cours/(?P<id_cours>[-a-zA-Z\d]+)/delete$', escapad_formulaire.views.delete_course, name='delete_course'),
    url(r'^cours/(?P<id_cours>[-a-zA-Z\d]+)/(?P<url>[-a-zA-Z\d]+)$', escapad_formulaire.views.cours_edition, name='cours_edition'),
    url(r'^cours/(?P<id_cours>[-a-zA-Z\d]+)/(?P<url>[-a-zA-Z\d]+)/delete$', escapad_formulaire.views.delete_module, name='delete_module'),

    


    url(r'^change_password/$', auth_views.password_change, {'template_name' : 'escapad_formulaire/password/password_change_form.html','post_change_redirect' : '/password_changed/'}),
    url(r'^password_changed/$', auth_views.password_change_done, {'template_name' : 'escapad_formulaire/password/password_change_done.html'}),

    url(r'^password_reset/$', auth_views.password_reset,
    {'template_name':'escapad_formulaire/password/password_reset_form.html',
    'post_reset_redirect' : '/password_reset/done/',
    'email_template_name':'escapad_formulaire/password/password_reset_email.html'}, name='password_reset'),

    url(r'^password_reset/done/$', auth_views.password_reset_done,
    {'template_name':'escapad_formulaire/password/password_reset_done.html'},name='password_reset_done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    auth_views.password_reset_confirm,
    {'template_name':'escapad_formulaire/password/password_reset_confirm.html'}, name='password_reset_confirm'),

    url(r'^reset/done/$', auth_views.password_reset_complete,
    {'template_name':'escapad_formulaire/password/password_reset_complete.html'}, name='password_reset_complete'),



]

admin.site.site_header = 'Esc@pad Admin'
admin.site.site_title = 'Esc@pad Admin'
