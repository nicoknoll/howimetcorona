from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    re_path(r'^check/?$', views.CheckView.as_view(), name='check'),
    re_path(r'^report/?$', views.ReportView.as_view(), name='report'),
]
