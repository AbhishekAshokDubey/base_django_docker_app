from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^gettext$', views.get_text, name='get_text'),
    url(r'^uploadresult$', views.upload_result, name='upload_result'),
]