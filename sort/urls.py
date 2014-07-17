from django.conf.urls import patterns, url

from sort import views

urlpatterns = patterns('',
    url(r'^pairwise$', views.index, name='index'),
    url(r'^rank$', views.rank, name='rank'),
    url(r'^export$', views.export, name='export'),
    url(r'^individual$', views.individual, name='individual'),
    url(r'^pairwise_raw$', views.pairwise_raw, name='pairwise_raw'),
    url(r'^individual_raw$', views.individual_raw, name='individual_raw'),
    url(r'^graph$', views.graph, name='graph'),
    url(r'^vote/(?P<first>[0-9]+)/(?P<second>[0-9]+)/(?P<value>-?[0-9]+)$', views.vote, name='vote'),
    url(r'^vote_individual/(?P<obj_id>[0-9]+)/(?P<value>-?[0-9]+)$',
        views.vote_individual, name='vote_individual'),
)
