"""cityscorewebapp URL Configuration

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
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import *
from django.contrib import admin
# from cityscore import urls
from cityscore.cityscore import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cityscore'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^metric/$', views.get_metric, name = 'get_metric'),
    url(r'^login/$', views.login_pls, name = 'login_pls'),
    url(r'cityscore/$', views.today_view, name = 'today_view'),
    url(r'index/$', views.welcome_city, name = 'welcome_city'),
    url(r'^entry/$',views.get_value, name = 'get_value'),
    url(r'attn/$', views.attn, name = 'attn'),
    url(r'^register/$', views.register, name = 'register'),
    url(r'legend/$', views.legend, name = 'legend')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 