from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
from .models import *
import json
class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        # Join the chatroom group
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        self.accept()

        # Mark all unseen messages as seen when this user connects (for other members, not the sender)
        self.mark_all_unseen_as_seen()

    def disconnect(self, close_code):
        # Leave the chatroom group
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['message']

        # Create a new message with is_seen=False initially
        message = GroupMessage.objects.create(
            group=self.chatroom,
            author=self.user,
            body=body,
            is_seen=False  # Initially set to unseen
        )

        # Notify other members in the group
        event = {
            'type': 'message_handler',
            'message_id': message.id,
            'sender_id': self.user.id  # Pass the sender's ID
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)

        # Get the sender_id safely
        sender_id = event.get('sender_id')

        # Only update seen status for other users (not the sender)
        if sender_id and self.user.id != sender_id:
            message.is_seen = True
            message.save(update_fields=['is_seen'])  # Save the updated status

        context = {
            'message': message,
            'user': self.user
        }

        html = render_to_string('chat/chat_partials.html', context=context)
        self.send(text_data=html)

    def mark_all_unseen_as_seen(self):
        # Mark all unseen messages in the chatroom as seen (but not for the sender)
        unseen_messages = GroupMessage.objects.filter(
            group=self.chatroom,
            is_seen=False
        ).exclude(author=self.user)  # Exclude the sender's own messages

        for message in unseen_messages:
            message.is_seen = True
            message.save(update_fields=['is_seen'])