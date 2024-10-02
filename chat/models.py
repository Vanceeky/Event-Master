from django.db import models
from django.contrib.auth.models import User
import shortuuid

import random
import string

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
    body = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.body}"
    
    class Meta:
        ordering = ["-created_at"]
