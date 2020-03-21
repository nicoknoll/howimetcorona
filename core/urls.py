from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    re_path(r'^check/?$', views.CheckView.as_view(), name='check'),
    re_path(r'^check/map/?$', views.MapView.as_view(), name='map'),
    re_path(r'^report/?$', views.ReportView.as_view(), name='report'),
    re_path(r'^report/confirmation/(?P<upload_id>[0-9a-f-]{36})/?$', views.ReportConfirmationView.as_view(), name='report-confirmation'),
    re_path(r'^delete/?$', views.DeleteView.as_view(), name='delete'),
    re_path(r'^delete/confirmation/?$', views.DeleteConfirmationView.as_view(), name='delete-confirmation'),
]

