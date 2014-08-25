from django.conf.urls import patterns, url

from reqApp import views

urlpatterns = patterns('',
    url(r'^$' , 'django.contrib.auth.views.login',
        {'template_name':'reqApp/index.html'}, name='login'),
    url(r'^logout/$' , 'django.contrib.auth.views.logout_then_login',
        name='logout'),

    url(r'^usuario/$', views.editUser, name='editUser'),
    url(r'^pass/$', views.editPass, name='pass'),
    
    url(r'^proyecto/$', views.selectProject, name='PR'),

    url(r'^proyecto/TU/$', views.viewUT, name='UT'),
    url(r'^proyecto/RU/$', views.viewUR, name='UR'),
    url(r'^proyecto/RS/$', views.viewSR, name='SR'),
    url(r'^proyecto/MD/$', views.viewMD, name='MD'),
    url(r'^proyecto/CP/$', views.viewTC, name='TC'),
    url(r'^proyecto/HT/$', views.viewIC, name='IC'),
    
    url(r'^proyecto/contenido/$', views.getElementContent, name='elemContent'),
    
    url(r'^documentos/requisitos/$', views.docReq, name='docReq'),
    url(r'^documentos/diseno/$', views.docDsn, name='docDsn'),
    url(r'^documentos/casos_de_prueba/$', views.docTC, name='docTC'),
    url(r'^documentos/historico/$', views.docHis, name='docHis'),
    
    url(r'^herramientas/tareas/$', views.tasks, name='tasks'),
    url(r'^herramientas/estadisticas/$', views.statistics, name='statistics'),
    url(r'^herramientas/matrices/$', views.matrices, name='matrices'),
    url(r'^herramientas/consistencia/$', views.consistency, name='consistency'),
    url(r'^herramientas/bitacora/$', views.registry, name='registry'),
    
    url('^upload/img/$', views.imgUpload, name='mce_upload_image'),
    
    url(r'pdf/$', views.pdf, name='pdf'),
    
    url(r'^ayuda/$', views.help, name='help'),
)
