from django.shortcuts import render

# Create your views here.



def customer_login_page(request):
    return render(request, 'authentication/login.html')


def customer_register_page(request):
    return render(request, 'authentication/register.html')



def provider_login_page(request):
    return render(request, 'authentication/provider_login.html')

def provider_register_page(request):
    return render(request, 'authentication/provider_register.html')
