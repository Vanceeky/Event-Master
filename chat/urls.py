from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),

    path('chat/messages/<int:group_id>/', views.get_chat_messages, name='get_chat_messages'),

    path('chat/', views.chat_view, name='chat'),

    path('chat/<username>/', views.get_or_create_chatroom, name='start-chat'),
    
    path('chat/room/<chatroom_name>/', views.chat_view, name='chatroom'),
    path('chat/fileupload/<chatroom_name>/', views.chat_file_upload, name='chat-file-upload'),





    path('api/chat-groups/', views.user_chat_groups, name='user_chat_groups'),
    path('api/chat-groups/<int:group_id>/messages/', views.fetch_group_messages, name='fetch_chat_messages'),


]
