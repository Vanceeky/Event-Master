from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    #ADMIN PATHS
    path('dashboard/', views.dashboard, name='admin-dashboard'),
]
