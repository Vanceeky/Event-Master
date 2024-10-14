from django.db import models
from django.contrib.auth.models import User
import shortuuid

import random
import string
import os

def generate_random_chars(length=8):
    characters = string.ascii_letters + string.digits  # Exclude special characters
    return ''.join(random.choice(characters) for _ in range(length))

# Create your models here.
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, default=generate_random_chars)
    users_online = models.ManyToManyField(User, related_name ="online_in_groups", blank=True)
    members = models.ManyToManyField(User, related_name="chat_groups", blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name="chat_messages", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=512, null=True, blank = True)
    file = models.FileField(upload_to='group_messages', null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
        

    def __str__(self):
        if self.body:
            return f"{self.author.username}: {self.body}"
        elif self.file:
            return f"{self.author.username}: {self.file}"
    
    class Meta:
        ordering = ["-created_at"]

    @property
    def is_image(self):
        if self.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', 'svg', '.webp', '.tiff', '.bmp', '.jfif')):
            return True
        else:
            return False
