from django.conf.urls import url
from django.contrib import admin
from myapp.views import *
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^vendedor/$', vendedor, name="vendedor"),
    url(r'^admin/', admin.site.urls)
]
