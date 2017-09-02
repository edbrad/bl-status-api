from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.root),
    url(r'^authenticate/$', views.authenticate, name='authenticate'),
    url(r'^check-token-exp/$', views.check_token_exp, name='check_token_exp'),
    url(r'^all-statuses/$', views.all_statuses, name='all_statuses'),
    url(r'^status-count/$', views.status_count, name='status_count'),
    url(r'^find-one-by-pattern/$', views.find_one_by_pattern, name='find_one_by_pattern'),
    url(r'^find-many-by-pattern/$', views.find_many_by_pattern, name='find_many_by_pattern'),
    url(r'^insert-one/$', views.insert_one, name='insert_one'),
    url(r'^insert-many/$', views.insert_many, name='insert_many'),
    url(r'^update-one/$', views.update_one, name='update_one'),
    url(r'^delete-one-by-pattern/$', views.delete_one_by_pattern, name='delete_one_by_pattern'),
    url(r'^delete-many-by-pattern/$', views.delete_many_by_pattern, name='delete_many_by_pattern'),
    url(r'^file-upload/$', views.file_upload, name='file_upload'),
    url(r'^logs/$', views.client_logs, name='client_logs'),
    url(r'^docs/', include('rest_framework_docs.urls')),
]