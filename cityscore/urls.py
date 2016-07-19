"""cityscore URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from cityscore import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'cityscore'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^/enter_val/$', views.enter_val,name = 'enter_val'),
    url(r'^/new_metric/$', views.new_metric, name = 'new_metric'),
    url(r'^/login/$', views.login_pls, 'login'),
    url(r'/cityscore/$', views.today_view, 'today_view'),
    url(r'/welcome_city/$', views.welcome_city, 'welcome_city'),
    url(r'^/register/$', views.register, 'register')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
