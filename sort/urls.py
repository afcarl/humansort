from django.conf.urls import patterns, url

from sort import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^rank$', views.rank, name='rank'),
    url(r'^vote/(?P<first>[0-9]+)/(?P<second>[0-9]+)/(?P<value>-?[0-9]+)$', views.vote, name='vote'),
)
