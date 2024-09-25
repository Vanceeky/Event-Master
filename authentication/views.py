from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from base.models import Customer
from django.contrib import messages
from django.contrib.auth import authenticate, login
# Create your views here.
from django.contrib.auth.models import Group
from base.models import ServiceProvider, Service, ServiceImage
from django.db import transaction, IntegrityError

import random
import string
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from base.models import ServiceProvider

def generate_password(length=10):
    characters = string.ascii_letters + string.digits  # No special characters
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def customer_login_page(request):
    return render(request, 'authentication/login.html')


def customer_register_page(request):
    return render(request, 'authentication/register.html')

def register_customer(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(username=email, first_name=firstname, last_name=lastname, email=email, password=password)
        user.save()
        
        # Create a customer record
        customer = Customer.objects.create(user=user)
        customer.save()
      
        customer_group, created = Group.objects.get_or_create(name='customer')
        user.groups.add(customer_group)

        messages.success(request, 'Account created successfully! Please login to continue.')
        return redirect('customer-login') 


    return render(request, 'authentication/register.html')


def login_customer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
      
            if user.groups.filter(name='customer').exists():
                login(request, user)
                return redirect('customer-account') 
            else:
                messages.error(request, 'You do not have customer access.')
                return redirect('customer-login')  
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('customer-login')


    return render(request, 'authentication/login.html')




def provider_login_page(request):
    return render(request, 'authentication/provider_login.html')

def provider_register_page(request):
    return render(request, 'authentication/provider_register.html')

def register_provider(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                email = request.POST.get('email')

                # Generate a password
                password = generate_password()

                user = User.objects.create_user(username=email, first_name=firstname, last_name=lastname, email=email, password=password)

                # Create a provider record
                provider = ServiceProvider.objects.create(
                    user=user,
                    name=request.POST.get('business_name'),
                    contact_number=request.POST.get('contact_number'),
                    address=request.POST.get('address'),
                    desc=request.POST.get('business_description')
                )

                if request.FILES.get('logo'):
                    provider.logo = request.FILES['logo']

                provider.save()

                provider_group, created = Group.objects.get_or_create(name='provider')
                user.groups.add(provider_group)

                service = Service.objects.create(
                    provider=provider,
                    name=request.POST.get('service_name'),
                    price=request.POST.get('price'),
                    description=request.POST.get('description'),
                    inclusions=request.POST.get('inclusions'),
                    category=request.POST.get('category'),
                )

                if request.FILES.getlist('service_images'):
                    for img in request.FILES.getlist('service_images'):
                        service_image = ServiceImage(service=service, image=img)
                        service_image.save()

                # Send email with the generated password
                email_subject = 'Welcome to Our Service! Your Account Has Been Created'
                email_message = f'''
                Dear {firstname},

                Thank you for registering with us! We're excited to have you on board.

                Your account has been successfully created. Below are your login credentials:

                **Email:** {email}
                **Password:** {password}

                If you have any questions or need assistance, feel free to reach out to our support team.

                Best regards,
                The Event Master Team
                '''
                send_mail(email_subject, email_message, 'noreply@event_master.com', [email])

                messages.success(request, 'Account created successfully! Please check your email for the password.')
                return JsonResponse({'success': True, 'message': 'Account created successfully! Please check your email for the password.'}, status=200)

        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'A user with this email already exists. Please use a different email.'}, status=400)

        except ValidationError as e:
            return JsonResponse({'success': False, 'message': 'There were validation errors.', 'errors': e.messages}, status=422)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")  # Debugging
            return JsonResponse({'success': False, 'message': 'An unexpected error occurred. Please try again later.', 'error': str(e)}, status=500)

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

def login_provider(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
           
            if user.groups.filter(name='provider').exists():
                login(request, user)

                provider = ServiceProvider.objects.get(user=user)


                return redirect('service-provider', provider_id=provider.id)  
            
            else:
                messages.error(request, 'You do not have provider access.')
                return redirect('provider-login')  
            
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('provider-login')


    return render(request, 'authentication/provider_login.html')







def logout_view(request):
    logout(request)  
    return redirect('index') 
