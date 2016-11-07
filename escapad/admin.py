
import os

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.conf import settings

# Register your models here.
from .models import Repository
from .forms import RepositoryForm


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('repository',  'repo_synced', 'default_branch', 'last_compiled', 'git_url', 'build_url', 'site_url', )
    readonly_fields = ('slug', 'git_username', 'git_name', 'repo_synced', 'last_compiled','provider','site_url_long', 'build_url_long', )
    form = RepositoryForm

    def get_readonly_fields(self, request, obj):
        self.request = request
        return super(RepositoryAdmin, self).get_readonly_fields(request, obj)

    def repository(self, obj):
        return '%s/%s' % (obj.git_username, obj.git_name)

    def build_url(self, obj):
        url = reverse('build_repo', args=(obj.slug,))
        return '<a href="%s" target="_blank">%s<a>' % (url, 'build')
    build_url.allow_tags = True
    build_url.short_description = 'Build link'

    def build_url_long(self, obj):
        """ used in detailed view """
        if obj.slug:
            url = self.request.build_absolute_uri(reverse('build_repo', args=(obj.slug,)))
            return '<a href="%s" target="_blank">%s<a>' % (url, url)
        else:
            return ''
    build_url_long.allow_tags = True
    build_url_long.short_description = 'Build link'

    def site_url(self, obj):
        url = reverse('visit_site', args=(obj.slug,))
        return '<a href="%s">%s<a>' % (url, 'visit')
    site_url.allow_tags = True
    site_url.short_description = 'Site link'

    def site_url_long(self, obj):
        if obj.slug:
            url = self.request.build_absolute_uri(reverse('visit_site', args=(obj.slug,)))
            return '<a href="%s" target="_blank">%s<a>' % (url, url)
        else:
            return ''
    site_url_long.allow_tags = True
    site_url_long.short_description = 'Site link'

admin.site.register(Repository, RepositoryAdmin)
