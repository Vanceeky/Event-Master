from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.customer_login_page, name='customer-login'),
    path('register/', views.customer_register_page, name='customer-register'),
]
