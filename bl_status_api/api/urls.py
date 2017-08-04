from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.root),
    url(r'^all-statuses/$', views.all_statuses, name='all_statuses'),
    url(r'^status-count/$', views.status_count, name='status_count'),
    url(r'^find-one-by-pattern/$', views.find_one_by_pattern, name='find_one_by_pattern'),
    url(r'^find-many-by-pattern/$', views.find_many_by_pattern, name='find_many_by_pattern'),
]