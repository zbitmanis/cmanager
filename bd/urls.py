"""hmfk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from .views import login,change_password,osd_chart,osd_stats,reweight_osd,set_osd_criteria,obtain_new_chart_data, generation_chart, status, start, pause, reset
#from chart import osd_chart

urlpatterns = [
    url(r'^login/$', login, name="login"),
    url(r'^$', login, name="cview"),
    url(r'^osd_chart/$', osd_chart, name="osd_chart"),
    url(r'^status/$', status, name="status"),
    url(r'^start/$', start, name="start"),
    url(r'^pause/$', pause, name="pause"),
    url(r'^reset/$', reset, name="reset"),
    url(r'^obtain_new_chart_data/$', obtain_new_chart_data, name="obtain_new_chart_data"),
    url(r'^osd_chart/(?P<records>\d+?)$', osd_chart, name="osd_chart"),
    url(r'^generation_chart/$', generation_chart, name="generation_chart"),
    url(r'^generation_chart/(?P<records>\d+?)$', generation_chart, name="generation_chart"),
    url(r'^osd_stats/$', osd_stats, name="osd_stats"),
    url(r'^reweight_osd/$', reweight_osd, name="reweight_osd"),
    url(r'^reweight_osd/(?P<osd_id>\d+?)/(?P<weight>\d+\.\d+)/$', reweight_osd, name="reweight_osd"),
    url(r'^reweight_osd/(?P<osd_id>\d+?)/(?P<weight>\d+)/$', reweight_osd, name="reweight_osd"),
    url(r'^reweight_osd/(?P<osd_id>\d+?)/(?P<weight>\d+\.\d+)/$', reweight_osd, name="reweight_osd"),
    url(r'^set_osd_criteria/(?P<osd_id>\d+?)/(?P<optim>\d+?)/$', set_osd_criteria, name="set_osd_criteria"),
    url(r'^change_password/$', change_password,name="change_password"),
]
