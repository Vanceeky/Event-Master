from django.contrib import admin
from . models import *



# Register your models here.



admin.site.site_title = 'Event Master Administration'
admin.site.site_header = 'Event Master'


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'desc', 'contact_number', 'address')
    search_fields = ('name', 'desc', 'user')


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