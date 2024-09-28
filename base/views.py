from django.shortcuts import render
from . models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# Create your views here.

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
    provider = get_object_or_404(ServiceProvider, id=provider_id) 
    
    services = Service.objects.filter(provider=provider)
    
    #service_posts = ServicePost.objects.filter(service__in=services).prefetch_related('images')
    service_posts = ServicePost.objects.filter(created_by=provider).prefetch_related('images')

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
    
    
