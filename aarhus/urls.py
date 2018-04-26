from django.conf.urls import patterns, include, url

from django.contrib import admin
from notebook import views


import autocomplete_light
# import every app/autocomplete_light_registry.py
autocomplete_light.autodiscover()

admin.autodiscover()
admin.site.site_header = 'Aarhus Notebook administration'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aarhus.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$',views.index, name='index'),
    url(r'^notebook/', include('notebook.urls')),
   # url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^admin/', include(admin.site.urls))
)
