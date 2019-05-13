from django.urls import path, re_path
from reacttools import views
from django.conf import settings

urlpatterns = [
    re_path('proxy/(\w.+)$', views.proxy, name='reacttools-proxy'),
]
