from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/?$', views.user_login, name='login'),
    url(r'^logout/?$', views.user_logout, name='logout'),
    url(r'^register/?$', views.register, name='register'),
    url(r'^get_folder/', views.get_folder),
    url(r'^get_file/', views.get_file),
    url(r'^esgf_search/', views.esgf_search),
    url(r'^vtk/', views.vtkweb_launcher),
]
