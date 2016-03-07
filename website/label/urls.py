from django.conf.urls import include, url, patterns
from django.contrib import admin
import label.views

urlpatterns = patterns("label.views",
	# url(r'^$', 'login', name="login"),
    url(r'^login', 'login', name="login"),
    url(r'^index/(?P<url_category>[\w]+)/(?P<uid>[0-9]{1})/(?P<pid>[0-9]+)/$', 'index', name="index"),
    url(r'^list/(?P<url_category>[\w]+)/(?P<uid>[0-9]{1})/$', 'list', name="list"),
    # url(r'^read/', 'read', name="read"),
    url(r'^update/(?P<url_category>[\w]+)/(?P<uid>[0-9]{1})/(?P<pid>[0-9]+)/(?P<label>[\w\s/&();.-]+)/$', 'update', name="update"),
    url(r'^compare/(?P<url_category>[\w]+)/$', 'compare', name="compare"),
    url(r'^next/(?P<url_category>[\w]+)/$', 'next', name="next"),
    # url(r'^delete/', 'delete', name="delete"),
)