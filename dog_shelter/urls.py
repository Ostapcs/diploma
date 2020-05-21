from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^dogs/$', views.dogs_list_view, name='dogs'),
    url(r'^user/(?P<pk>\d+)$', views.update_user_view, name='user-info'),
    url(r'^organizations/$', views.OrganizationsListView.as_view(), name='organizations'),
    url(r'^organization/(?P<pk>\d+)$', views.organization_info_view, name='org-info'),
    # url(r'^organizations/(?P<pk>\d+)/update/$', views.o, name='org_update'),
    url(r'^register/$', views.register_user_view, name='register'),
    url(r'^dog/create/$', views.create_dog_view, name='dog_create'),
    url(r'^dog/(?P<pk>\d+)$', views.dog_info_view, name='dog-info'),
    url(r'^dog/(?P<pk>\d+)/update/$', views.dog_update_view, name='dog_update'),
    url(r'^dog/(?P<pk>\d+)/delete/$', views.DogDelete.as_view(), name='dog_delete'),
    url(r'^like/$', views.user_likes_dog_view, name='user_like')
]
