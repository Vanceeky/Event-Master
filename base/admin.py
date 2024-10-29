from django.contrib import admin
from . models import *

from django.urls import reverse

# Register your models here.



admin.site.site_title = 'Event Master Administration'
admin.site.site_header = 'Event Master'
from django.contrib.admin import SimpleListFilter
from django.core.mail import send_mail
from django.conf import settings

class ActiveStatusFilter(SimpleListFilter):
    title = 'Account Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Active':
            return queryset.filter(user__is_active=True)
        if self.value() == 'Inactive':
            return queryset.filter(user__is_active=False)
        return queryset
    

class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'contact_number', 'address', 'is_active')
    list_filter = (ActiveStatusFilter,)  
    actions = ['activate_users']

    def is_active(self, obj):
        return obj.user.is_active
    is_active.boolean = True  

    def activate_users(self, request, queryset):
        for service_provider in queryset:
            service_provider.user.is_active = True
            service_provider.user.save()
            
            # Construct the activation URL
            login_url = request.build_absolute_uri(reverse('provider-login')) 
            
            # Send activation email
            send_mail(
                'Your Account is Now Active',
                'Hello {},\n\nYour account has been successfully activated! You can now log in to your account using the following link:\n\n{}'.format(service_provider.name, login_url),
                settings.EMAIL_HOST_USER, 
                [service_provider.user.email],  
                fail_silently=False,
            )
            
        self.message_user(request, "Selected service providers have been activated and notified via email.")
    activate_users.short_description = "Activate selected service providers"

# Register the admin class with the associated model
admin.site.register(ServiceProvider, ServiceProviderAdmin)



class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ('image', 'caption')

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1
    fields = ('author', 'score', 'content', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('provider', 'name', 'description', 'category', 'price')
    search_fields = ('name', 'description', 'category')
    list_filter = ('provider',)
    inlines = [ServiceImageInline, RatingInline]


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image', 'caption')

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)



@admin.register(ServicePost)
class ServicePostAdmin(admin.ModelAdmin):
    list_display = ('title',  'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ( 'created_by', 'created_at')
    inlines = [PostImageInline, CommentInline]



'''
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')
    list_filter = ('post', 'author')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'score', 'created_at')
    search_fields = ('post__title', 'author__username', 'score')
    list_filter = ('post', 'author', 'score')


'''


admin.site.register(Customer)
    
class SelectedServiceInline(admin.TabularInline):
    model = SelectedService
    extra = 1
    fields = ('service', 'status')
    autocomplete_fields = ('service',)  # Optional: improves the UI for selecting services

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'event_date', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('customer', 'event_date')
    inlines = [SelectedServiceInline]