from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.customer_login_page, name='customer-login'),
    path('register/', views.customer_register_page, name='customer-register'),


    path('register-customer/', views.register_customer, name='register-customer'),

    path('login-customer/', views.login_customer, name='login-customer'),




    path('service-provider/register/', views.provider_register_page, name='provider-register'),
    path('service-provider/login/', views.provider_login_page, name='provider-login'),

    path('service-provider/register-provider/', views.register_provider, name='register-provider'),
    path('service-provider/login-account/', views.login_provider, name='login-provider'),


    path('logout/', views.logout_view, name='logout'),

]
