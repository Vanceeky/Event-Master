from django.shortcuts import render, redirect
from . models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.db.models import Count
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from chat.models import ChatGroup, GroupMessage


def index(request):
    service_providers = ServiceProvider.objects.all()[:5]
    customers = Customer.objects.all()
    services = Service.objects.all()
    providers = ServiceProvider.objects.all()
    services_ = Service.objects.all()

    provider = None  
    if request.user.is_authenticated:
        try:
            provider = ServiceProvider.objects.get(user=request.user)
        except ServiceProvider.DoesNotExist:
            provider = None  

    context = {
        'service_providers': service_providers,
        'customers': customers,
        'services': services,
        'providers': providers,
        'services_': services_,
        'provider': provider,
    }
    return render(request, 'index.html', context)



def inbox(request):
    return render(request, 'base/inbox.html')

def dashboard(request):
    return render(request, 'base/admin/dashboard.html')




# Service Provider Views



def service_provider(request, provider_id):

    user = User.objects.get(id=provider_id)
    provider = get_object_or_404(ServiceProvider, user=user) 

    
    # Prefetch services and related images
    services = Service.objects.filter(provider=provider).prefetch_related('images')
    
    #service_posts = ServicePost.objects.filter(service__in=services).prefetch_related('images')
    service_posts = ServicePost.objects.filter(created_by=provider).prefetch_related('comments', 'images')
    
    for service in services:
        inclusions_list = service.inclusions.split(',') if service.inclusions else []

        service.inclusions_list = [inclusion.strip() for inclusion in inclusions_list]

    context = {
        'provider': provider,
        'services': services,
        'service_posts': service_posts
    }

    return render(request, 'base/provider/home.html', context)


def create_service(request):
    if request.method == 'POST':
        provider_id = request.POST.get('provider_id')
        service_name = request.POST.get('service_name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        inclusions = request.POST.get('inclusions')


        if not all([provider_id, service_name, price, description, inclusions]):
            return JsonResponse({'message': 'All fields are required.'}, status=400)


        provider = get_object_or_404(ServiceProvider, id=provider_id)

        try:
            Service.objects.create(
                provider=provider,
                name=service_name,
                price=price,
                description=description,
                inclusions=inclusions
            )
            return JsonResponse({'message': 'Service created successfully'})
        except Exception as e:
            return JsonResponse({'message': f'Error creating service: {str(e)}'}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

def create_post(request):
    if request.method == 'POST':
        provider_id = request.POST.get('provider_id')
        title = request.POST.get('post_title')
        description = request.POST.get('description')
        

        post = ServicePost(
            created_by_id=provider_id, 
            title=title,
            description=description
        )
        post.save()

        # Handle file uploads
        images = request.FILES.getlist('post_images')
        for image in images:
            PostImage.objects.create(
                post=post,
                image=image
            )
        
        # Success response
       # messages.success(request, 'Post created successfully!')
        return JsonResponse({'message': 'Post created successfully!'}, status=200)
    
    # Return an error response if method is not POST
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def provider_bookings(request):
    provider = ServiceProvider.objects.get(user=request.user)

   
    selected_services = SelectedService.objects.filter(
        service__provider=provider
    ).exclude(status='draft').select_related('event').prefetch_related('event__customer')

  
    events_dict = {}
    for service in selected_services:
        event = service.event
        if event not in events_dict:
            events_dict[event] = {
                'event': event,
                'services': []
            }
        events_dict[event]['services'].append(service)

    context = {
        'provider': provider,
        'events': events_dict.values(),  
    }

    return render(request, 'base/provider/bookings.html', context)


# CUSTOMER VIEWS

def home_services(request):
    services = Service.objects.all()

    for service in services:
        inclusions_list = service.inclusions.split(',') if service.inclusions else []

        service.inclusions_list = [inclusion.strip() for inclusion in inclusions_list]
        
    context = {
        'services': services
    }

    return render(request, 'base/home_services.html', context)

def service_details(request, service_id):
    service = get_object_or_404(Service, id=service_id)


    inclusions_list = service.inclusions.split(',') if service.inclusions else []

    service.inclusions_list = [inclusion.strip() for inclusion in inclusions_list]

    images = service.images.all()

    category = service.category

    related_services = Service.objects.filter(category=category).exclude(id=service_id)

    context = {
        'service': service,
        'images': images,
        'services': related_services
    }

    return render(request, 'base/service_details.html', context)


def added_service_page(request):

    customer = Customer.objects.get(user = request.user)
    events = Event.objects.filter(customer=customer).prefetch_related('selected_services__service')
    
    for event in events:
        for selected_service in event.selected_services.all():
            inclusions = selected_service.service.inclusions
            if inclusions:
                # Split the inclusions by comma and strip any extra spaces
                selected_service.service.inclusions_list = [inclusion.strip() for inclusion in inclusions.split(',')]
            else:
                selected_service.service.inclusions_list = []
    context = {
        'customer': customer,
        'events': events
    }

    return render(request, 'base/customer/added_service.html', context)



# CUSTOMER ACCOUNT VIEWS

def customer_account(request):

    customer = Customer.objects.get(user = request.user)
    events = Event.objects.filter(customer=customer).prefetch_related('selected_services__service')
    
    for event in events:
        for selected_service in event.selected_services.all():
            inclusions = selected_service.service.inclusions
            if inclusions:
                # Split the inclusions by comma and strip any extra spaces
                selected_service.service.inclusions_list = [inclusion.strip() for inclusion in inclusions.split(',')]
            else:
                selected_service.service.inclusions_list = []
    context = {
        'customer': customer,
        'events': events
    }



    return render(request, 'base/customer/account.html', context)

def fetch_events(request):
    customer = Customer.objects.get(user=request.user)
    
    events = Event.objects.filter(customer=customer, status__in=['draft', 'pending'])
    
    event_data = list(events.values('id', 'title', 'event_date'))
    
    return JsonResponse({'events': event_data})


def add_service_to_event(request):
    try:
        if request.method == 'POST':
            event_id = request.POST.get('event_id')
            service_id = request.POST.get('service_id')

        # Retrieve the event and service objects
        event = get_object_or_404(Event, id=event_id)
        service = get_object_or_404(Service, id=service_id)

        # Check if the service is already added to the event
        if SelectedService.objects.filter(event=event, service=service).exists():
            return JsonResponse({'message': 'Service is already added to this event'}, status=400)
        
        # Create a new SelectedService object
        selected_service = SelectedService(event=event, service=service)
        selected_service.save()

        return JsonResponse({'message': 'Service added to event successfully'})
    
    except Exception as e:
        # Return a JSON response with an error message if something goes wrong
        return JsonResponse({'message': str(e)}, status=500)
    
    

def create_new_event(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('event_name')
            event_date = request.POST.get('date')
            location = request.POST.get('location')
            budget = request.POST.get('budget')
            description = request.POST.get('description')

            # Validate input data if necessary
            if not title or not event_date or not location or not budget or not description:
                return JsonResponse({'message': 'All fields are required.'}, status=400)

            # Create a new event
            event = Event(
                customer=Customer.objects.get(user=request.user),
                title=title,
                event_date=event_date,
                location=location,
                budget=budget,
                description=description
            )
            event.save()

            return JsonResponse({'message': 'Event created successfully!'})

        except Exception as e:
            # Return a JSON response with an error message if something goes wrong
            return JsonResponse({'message': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    

def remove_service_from_event(request,  event_service_id):
    try:
        event_service = get_object_or_404(SelectedService, id=event_service_id)
        event_service.delete()
        return JsonResponse({'message': 'Service removed from event successfully'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)
    

def update_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        event.title = request.POST.get('event_name')
        event.event_date = request.POST.get('date')
        event.location = request.POST.get('location')
        event.budget = request.POST.get('budget')
        event.description = request.POST.get('description')
        
        event.save()

        return JsonResponse({'message': 'Event updated successfully'})
    
    return JsonResponse({'message': 'Invalid request'}, status=400)

def remove_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        event.delete()

        return JsonResponse({'message': 'Event removed successfully'})

    return JsonResponse({'message': 'Invalid request'}, status=400)


def providers(request):
    providers = ServiceProvider.objects.annotate(service_count=Count('services')).all()



    context = {
        'providers': providers
    }
    return render(request, 'base/providers.html', context)


def add_comment_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_content = request.POST.get('comment')
        
        post = get_object_or_404(ServicePost, id=post_id)

        # Create a new Comment instance
        comment = Comment(
            post=post,
            author=request.user,
            content=comment_content
        )
        comment.save()

        # Prepare response data
        response_data = {
            'message': 'Comment added successfully',
            'author': f"{comment.author.first_name} {comment.author.last_name}",
            'content': comment.content,
            'created_at': timezone.localtime(comment.created_at).strftime('%Y-%m-%d %H:%M:%S')  # Format the date if needed
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)







def submit_booking_request(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        selected_service_ids = request.POST.getlist('selected_services') 
        selected_services = SelectedService.objects.filter(id__in=selected_service_ids)

        for selected_service in selected_services:
            selected_service.status = 'pending'
            selected_service.save()

      
            chat_group = ChatGroup.objects.filter(
                is_private=True,
                members=request.user
            ).filter(members=selected_service.service.provider.user).first()

            if not chat_group:
                chat_group = ChatGroup.objects.create(is_private=True)
                chat_group.members.add(request.user, selected_service.service.provider.user)

        
            GroupMessage.objects.create(
                group=chat_group,
                author=request.user,
                body=(f"Hi {selected_service.service.provider.name}, I've just added your service '{selected_service.service.name}' "
                      f"for my event '{event.title}' on {event.event_date} at {event.location}. "
                      "Could you please take a look and confirm if everything is okay? Thank you!")
            )

  
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Your booking request has been submitted, and the service providers have been notified through chat.'})

        messages.success(request, "Your booking request has been submitted, and the service providers have been notified through chat.")
        return redirect('added-service-page')

    return redirect('added-service-page')




def inquire_service(request):
    if request.method == 'POST':
        provider = request.POST.get('provider')

        message = request.POST.get('message')

        service_provider = ServiceProvider.objects.get(id=provider)



        chat_group = ChatGroup.objects.filter(
            is_private=True,
            members=request.user
        ).filter(members=service_provider.user).first()

        if not chat_group:
            chat_group = ChatGroup.objects.create(is_private=True)
            chat_group.members.add(request.user, service_provider.user)

        GroupMessage.objects.create(
            group = chat_group,
            author = request.user,
            body = message,
        )

        return redirect('chatroom', chat_group.group_name)
    
    return redirect('chatroom', chat_group.group_name)

def accept_booking_request(request):
    if request.method == "POST":
        selected_service_ids = request.POST.getlist('selected_services')
        selected_services = SelectedService.objects.filter(id__in=selected_service_ids)

        for selected_service in selected_services:
            selected_service.status = 'accepted'
            selected_service.save()

           
            chat_group = ChatGroup.objects.filter(
                is_private=True,
                members=request.user
            ).filter(members=selected_service.event.customer.user).first()

            GroupMessage.objects.create(
                group=chat_group,
                author=selected_service.service.provider.user,
                body=(f"Hi, your booking request for "
                      f"'{selected_service.service.name}' for the event '{selected_service.event.title}' "
                      f"on {selected_service.event.event_date} has been accepted. Thank you!")
            )

        return JsonResponse({'success': True, 'message': 'The booking requests have been accepted.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def cancel_booking_request(request):
    if request.method == "POST":
        selected_service_ids = request.POST.getlist('selected_services')
        selected_services = SelectedService.objects.filter(id__in=selected_service_ids)

        for selected_service in selected_services:
            selected_service.status = 'rejected' 
            selected_service.save()

            
            chat_group = ChatGroup.objects.filter(
                is_private=True,
                members=request.user
            ).filter(members=selected_service.event.customer.user).first()

            GroupMessage.objects.create(
                group=chat_group,
                author=selected_service.service.provider.user,
                body=(f"Hi, your booking request for "
                      f"'{selected_service.service.name}' for the event '{selected_service.event.title}' "
                      f"on {selected_service.event.event_date} has been canceled. If you have any questions, "
                      f"please feel free to reach out. Thank you!")
            )

        return JsonResponse({'success': True, 'message': 'The booking requests have been canceled.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

