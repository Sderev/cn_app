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
from escapad import views

urlpatterns = [
    url(r'^escapad/', include('escapad.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^form_upload/$', views.form_upload, name='form_upload'),
]

admin.site.site_header = 'Esc@pad Admin'
admin.site.site_title = 'Esc@pad Admin'
