from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

# Create your models here.

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    logo = models.FileField(upload_to='service_providers', null = True, blank = True, default='/default_logo2.jpg')
    desc = models.TextField(max_length=500, null = True, blank = True)
    contact_number = models.CharField(max_length=11, null = True, blank = True)
    address = models.CharField(max_length=255, null = True, blank = True)


    

    def __str__(self):
        return self.name
    



    


class Service(models.Model):

    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    inclusions = models.TextField(blank=True, null=True)

    category_choices = [
        ('Photographer', 'Photographer'),
        ('Videographer', 'Videographer'),
        ('Catering', 'Catering'),
        ('Venue Rental', 'Venue Rental'),
        ('Master of Ceremony', 'Master of Ceremony'),
        ('Other', 'Other'),
    ]

    category = models.CharField(max_length=255, choices=category_choices, blank=True, null=True, default="Other")

    def __str__(self):
        return self.name
    
class ServiceImage(models.Model):

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='service_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f'Image for {self.service}'

class ServicePost(models.Model):
    created_by = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='service_provider', null = True, blank = True)

    title = models.CharField(max_length=255)
    description = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(ServicePost, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='service_post_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Image for {self.post}'

class Comment(models.Model):
    post = models.ForeignKey(ServicePost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

class Rating(models.Model):
    post = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='ratings')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField()  # Consider a range, e.g., 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating by {self.author} on {self.post}'



class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    

class Event(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    location = models.CharField(max_length=255, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('Completed', 'Completed'), ('pending', 'Pending')], default='draft')
    
    def __str__(self):
        return self.title
    

class SelectedService(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='selected_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='draft')

    def __str__(self):
        return f'{self.service.name} for {self.event.title}'
    
    