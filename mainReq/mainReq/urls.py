from django.conf.urls import patterns, include, url

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

handler404 = 'reqApp.views.handler404'

urlpatterns = patterns('',
    url(r'^', include('reqApp.urls', namespace="reqApp")),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
)
